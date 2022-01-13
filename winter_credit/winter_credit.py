"""Winter credit processing"""
import logging

import datetime
import time

from dateutil import parser
from yaml.events import MappingStartEvent
from hydro_api.services import Services
log = logging.getLogger(__name__)

class WinterCredit:
    """Winter Credit extra logic

    This class suplements Hydro API data by providing calculated values for pre_heat period, reference period detection
    as well as next event information.
    """
    def __init__(self):
        self.api = Services()
        self.config = self.api.auth.config
        self.events = {}
        self.event_in_progress = False
        self.last_update = 0
        self.refreshData()

    def refreshData(self):
        """Refresh data if data is older than the config event_refresh_seconds parameter"""
        log.debug("Cheking if we need to update the Data")
        if time.time() > (self.last_update + self.config.periods.event_refresh_seconds):
            log.debug("Refreshing data")
            self.data = self.api.getWinterCredit()
            events_data = self._getWinterCreditEvents()
            self.events = events_data['events']
            self.event_in_progress = events_data['event_in_progress']
            self.last_update = time.time()
        else:
            log.debug("Data is up to date")

    def getFutureEvents(self):
        """Return future events object

        :return: future events list

        :rtype: list
        """
        self.refreshData()
        future_events = []
        for future_ts in self.events['current_winter']['future']:
            future_events.append(self.events['current_winter']['future'][future_ts])

        return future_events

    def getAllEvents(self):
        """Return future and past events (Current winter only) object

        :return: events list

        :rtype: list
        """
        self.refreshData()
        events = []
        for future_ts in self.events['current_winter']['future']:
            events.append(self.events['current_winter']['future'][future_ts])
        for past_ts in self.events['current_winter']['past']:
            events.append(self.events['current_winter']['past'][past_ts])
        return events
    def getNextEvent(self):
        """Return next event object

        :return: next event object

        :rtype: dict
        """
        self.refreshData()
        return self.events['next']

    def getCurrentState(self):
        """Calculate current periods"""
        thisday = datetime.datetime.now()
        today = thisday.strftime("%Y-%m-%d")
        today_noon_ts = datetime.datetime.strptime(today+" 12:00:00", "%Y-%m-%d %H:%M:%S").timestamp()

        nextday = thisday + datetime.timedelta(days=1)
        tomorrow = nextday.strftime("%Y-%m-%d")
        tomorrow_noon_ts = datetime.datetime.strptime(tomorrow+" 12:00:00", "%Y-%m-%d %H:%M:%S").timestamp()

        anchor_start_offset = datetime.timedelta(hours=self.config.periods.anchor_start_offset)
        anchor_duration = datetime.timedelta(hours=self.config.periods.anchor_duration)

        today_peak_morning_start = datetime.datetime.strptime(today+" "+self.config.periods.morning_peak_start, "%Y-%m-%d %H:%M:%S")
        today_peak_morning_end = datetime.datetime.strptime(today+" "+self.config.periods.morning_peak_end, "%Y-%m-%d %H:%M:%S")
        today_peak_evening_start = datetime.datetime.strptime(today+" "+self.config.periods.evening_peak_start, "%Y-%m-%d %H:%M:%S")
        today_peak_evening_end = datetime.datetime.strptime(today+" "+self.config.periods.evening_peak_end, "%Y-%m-%d %H:%M:%S")
        
        today_anchor_morning_start = today_peak_morning_start - anchor_start_offset
        today_anchor_morning_end = today_anchor_morning_start + anchor_duration
        today_anchor_evening_start = today_peak_evening_start - anchor_start_offset
        today_anchor_evening_end = today_anchor_evening_start + anchor_duration

        '''
        Calculation for the next periods. Should probably be with getNextEvent but I am not sure of the best way to move it there
        '''
        if thisday.timestamp() <= today_peak_morning_end.timestamp():
            next_peak_period_start = today_peak_morning_start
            next_peak_period_end = today_peak_morning_end
        elif today_peak_morning_end.timestamp() <= thisday.timestamp() <= today_peak_evening_start.timestamp():
            next_peak_period_start = today_peak_evening_start
            next_peak_period_end = today_peak_evening_end
        elif thisday.timestamp() >= today_peak_evening_end.timestamp():
            next_peak_period_start = today_peak_morning_start + datetime.timedelta(days=1)
            next_peak_period_end = today_peak_morning_end + datetime.timedelta(days=1)
        
        next_anchor_period_start = next_peak_period_start - anchor_start_offset
        next_anchor_period_end = next_anchor_period_start + anchor_duration

        if today_peak_morning_start.timestamp() <= thisday.timestamp() <= today_peak_morning_end.timestamp():
            current_period = 'peak'
            current_period_time_of_day = 'peak_morning'
        elif today_peak_evening_start.timestamp() <= thisday.timestamp() <= today_peak_evening_end.timestamp():
            current_period = 'peak'
            current_period_time_of_day = 'peak_evening'
        elif today_anchor_morning_start.timestamp() <= thisday.timestamp() <= today_anchor_morning_end.timestamp():
            current_period = 'anchor'
            current_period_time_of_day = 'anchor_morning'
        elif today_anchor_evening_start.timestamp() <= thisday.timestamp() <= today_anchor_evening_end.timestamp():
            current_period = 'anchor'
            current_period_time_of_day = 'anchor_evening'
        else:
            current_period = 'normal'
            current_period_time_of_day = 'normal'

        pre_heat = False
        morning_event_today = False
        evening_event_today = False
        morning_event_tomorrow = False
        evening_event_tomorrow = False
        upcoming_event = False
        next_peak_critical = True
        next_event = self.getNextEvent()
        if 'pre_heat_start_ts' in next_event:
            if next_event['pre_heat_start_ts'] <= thisday.timestamp() <= next_event['pre_heat_end_ts']:
                pre_heat = True
        for event in self.getAllEvents():
            if 'date' in event:
                if event['date'] == today:
                   if event['start_ts'] < today_noon_ts:
                       morning_event_today = True
                   else:
                       evening_event_today = True
                elif event['date'] == tomorrow:
                    if event['start_ts'] < tomorrow_noon_ts:
                        morning_event_tomorrow = True
                    else:
                        evening_event_tomorrow = True
                if event['date'] == today:
                    if event['end_ts'] > thisday.timestamp():
                        next_peak_critical = True
                        
                if event['start_ts'] > thisday.timestamp():
                        upcoming_event = True

        if next_peak_critical == True:
            current_composite_state = current_period_time_of_day+"_critical"
        elif next_peak_critical == False:
            current_composite_state = current_period_time_of_day+"_normal"

        response = {
            'state': {
                'current_period': current_period,
                'current_period_time_of_day': current_period_time_of_day,
                'current_composite_state': current_composite_state,
                'critical': next_peak_critical,
                'event_in_progress': self.event_in_progress,
                'pre_heat': pre_heat,
                'upcoming_event': upcoming_event,
                'morning_event_today' : morning_event_today,
                'evening_event_today' : evening_event_today,
                'morning_event_tomorrow' : morning_event_tomorrow,
                'evening_event_tomorrow' : evening_event_tomorrow,
            },
           'next': {
                'peak': {
                    'start': next_peak_period_start.strftime(self.config.formats.datetime_format),
                    'end' : next_peak_period_end.strftime(self.config.formats.datetime_format),
                    'start_ts': next_peak_period_start.timestamp(),
                    'end_ts': next_peak_period_end.timestamp(),
                    'critical': next_peak_critical
                },
                'anchor': {
                    'start': next_anchor_period_start.strftime(self.config.formats.datetime_format),
                    'end' : next_anchor_period_end.strftime(self.config.formats.datetime_format),
                    'start_ts': next_anchor_period_start.timestamp(),
                    'end_ts': next_anchor_period_end.timestamp(),
                    'critical': next_peak_critical
                },
           },
            'anchor_periods': {
                'morning': {
                    'date': today_anchor_morning_start.strftime('%Y-%m-%d'),
                    'start': today_anchor_morning_start.strftime(self.config.formats.datetime_format),
                    'end': today_anchor_morning_end.strftime(self.config.formats.datetime_format),
                    'start_ts': today_anchor_morning_start.timestamp(),
                    'end_ts': today_anchor_morning_end.timestamp(),
                },
                'evening': {
                    'date': today_anchor_evening_start.strftime('%Y-%m-%d'),
                    'start': today_anchor_evening_start.strftime(self.config.formats.datetime_format),
                    'end': today_anchor_evening_end.strftime(self.config.formats.datetime_format),
                    'start_ts': today_anchor_evening_start.timestamp(),
                    'end_ts': today_anchor_evening_end.timestamp(),
                },
            },
            'peak_periods': {
                'morning': {
                    'date': today_peak_morning_start.strftime('%Y-%m-%d'),
                    'start': today_peak_morning_start.strftime(self.config.formats.datetime_format),
                    'end': today_peak_morning_end.strftime(self.config.formats.datetime_format),
                    'start_ts': today_peak_morning_start.timestamp(),
                    'end_ts': today_peak_morning_end.timestamp(),
                },
                'evening': {
                    'date': today_peak_evening_start.strftime('%Y-%m-%d'),
                    'start': today_peak_evening_start.strftime(self.config.formats.datetime_format),
                    'end': today_peak_evening_end.strftime(self.config.formats.datetime_format),
                    'start_ts': today_peak_evening_start.timestamp(),
                    'end_ts': today_peak_evening_end.timestamp(),
                }
            }
        }
        return response

    def _getWinterCreditEvents(self):
        """Return winter peak events in a more structured way
    
        :return:
    
        JSON Object with current_winter, past_winters and next event.
        Current winter have past and future events
        Events have timestamp as key (easier to sort) and have date, start hour, end hour
    
        :example:
    
            ::
    
                events = {
                            'current_winter': {
                                'past': { [event, ...] },
                                'future': { [event, ...] }
                            },
                            'past_winters': { [event, ...] },
                            'next': { [event, ...] }
                        }
                event = {
                            'timestamp': {
                                date: 'YYYY-MM-DD',
                                start : 'HH:MM:SS',
                                end: 'HH:MM:SS'
                        }

        :rtype: dict

        :notes:
    
        - The next event will be returned only when the current event is completed to avoid interfering with automations
        - The timestamp is the timestamp of the end of the event
        - Future events have a 'pre_heat' datetime as a helper for homeassistant pre-event automations (offset -3h)
        """
        ref_date = datetime.datetime.now()
        events = {
            'current_winter': {
                'past': {},
                'future': {}
            },
            'past_winters': {},
            'next': {}
        }
        if 'periodesEffacementsHivers' in self.data:
            for season in self.data['periodesEffacementsHivers']:
                winter_start = parser.isoparse(season['dateDebutPeriodeHiver']).date()
                winter_end = parser.isoparse(season['dateFinPeriodeHiver']).date()
                if winter_start <= datetime.date.today() <= winter_end:
                    current = True
                else:
                    current = False
    
                if 'periodesEffacementHiver' in season:
                    for event in season['periodesEffacementHiver']:
                        e = {}
                        date = parser.isoparse(event['dateEffacement'])
                        e['date'] = date.strftime('%Y-%m-%d')
                        e['start'] = date.strftime('%Y-%m-%d') + " " + event['heureDebut']
                        e['end'] = date.strftime('%Y-%m-%d') + " " + event['heureFin']
                        end_date_time = datetime.datetime.strptime(e['end'], '%Y-%m-%d %H:%M:%S')
                        start_date_time = datetime.datetime.strptime(e['start'], '%Y-%m-%d %H:%M:%S')
                        end_ts = end_date_time.timestamp()
                        start_ts = start_date_time.timestamp()
                        e['start_ts'] = start_ts
                        e['end_ts'] = end_ts
                        future = False
                        if end_date_time >= ref_date:
                            future = True
                        if current:
                            if future:
                                events['current_winter']['future'][end_ts] = e
                            else:
                                events['current_winter']['past'][end_ts] = e
                        else:
                            events['past_winter'][end_ts] = e
        next_event = self._getNextEvent(events, ref_date)
        events['next'] = next_event['next']

        return {'events': events, 'event_in_progress': next_event['event_in_progress']}

    def _getCurrentState(self):
        return {}

    def _getPreHeat(self, start):
        """Calculate pre_heat period according to event start date
    
        :param: start: datetime object reprensenting the start of the next event

        :return: pre_heat period

        :rtype: dict
        """
        pre_heat_start_offset = datetime.timedelta(hours=self.config.events.pre_heat_start_offset)
        pre_heat_start = start - pre_heat_start_offset
        pre_heat_end_offset = datetime.timedelta(hours=self.config.events.pre_heat_end_offset)
        pre_heat_end = start - pre_heat_end_offset
        pre_heat = {
            'pre_heat_start': pre_heat_start.strftime(self.config.formats.datetime_format),
            'pre_heat_end': pre_heat_end.strftime(self.config.formats.datetime_format),
            'pre_heat_start_ts': pre_heat_start.timestamp(),
            'pre_heat_end_ts': pre_heat_end.timestamp()
        }
        return pre_heat
    
    
    def _getNextEvent(self, events, ref_date):
        """Calculate the next events
    
        :param: events: the events object we have built from hydro API self.data
    
        :return: event object

        :rtype: dict
        """
    
        event_in_progress = False
        next_event_timestamp = None
        next_event = {}
        if events['current_winter']['future']:
            for timestamp in events['current_winter']['future']:
                event_start_datetime = datetime.datetime.strptime(events['current_winter']['future'][timestamp]['start']
                    , self.config.formats.datetime_format)
                event_end_datetime = datetime.datetime.strptime(events['current_winter']['future'][timestamp]['end']
                    , self.config.formats.datetime_format)
                pre_heat = self._getPreHeat(event_start_datetime)
                events['current_winter']['future'][timestamp]['pre_heat_start'] = pre_heat['pre_heat_start']
                events['current_winter']['future'][timestamp]['pre_heat_end'] = pre_heat['pre_heat_end']
                events['current_winter']['future'][timestamp]['pre_heat_start_ts'] = pre_heat['pre_heat_start_ts']
                events['current_winter']['future'][timestamp]['pre_heat_end_ts'] = pre_heat['pre_heat_end_ts']
    
                if event_start_datetime.timestamp() <= ref_date.timestamp() <= event_end_datetime.timestamp():
                    event_in_progress = True
                    next_event_timestamp = timestamp
                    break
    
            if not event_in_progress:
                next_event_timestamp = min(events['current_winter']['future'], key=float)
        if next_event_timestamp:
            next_event = events['current_winter']['future'][next_event_timestamp]

        return {'next': next_event, 'event_in_progress': event_in_progress}