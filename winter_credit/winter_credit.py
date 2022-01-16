"""Winter credit processing"""
import datetime
import logging
import time

from dateutil import parser

from hydro_api.services import Services
from .event import Event
from .period import Period

log = logging.getLogger(__name__)


class WinterCredit:
    """Winter Credit extra logic

    This class supplements Hydro API data by providing calculated values for pre_heat period, anchor period detection
    as well as next event information.
    """

    def __init__(self):
        self.api = Services()
        self.config = self.api.auth.config
        self.events = {}
        self.event_in_progress = False
        self.last_update = 0
        self._refreshData()

    def _refreshData(self):
        """Refresh data if data is older than the config event_refresh_seconds parameter"""
        # DATES
        self.ref_date = datetime.datetime.now()
        # To test the date can be modified artificially here.
        # self.ref_date = self._dateTimeFromString("2022-01-18 00:00:00")
        self.today = datetime.datetime.now()
        self.today_date = self.today.strftime("%Y-%m-%d")
        self.today_noon_ts = self._timestampFromString(self.today_date + " 12:00:00")

        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.tomorrow_date = self.tomorrow.strftime("%Y-%m-%d")
        self.tomorrow_noon_ts = self._timestampFromString(self.tomorrow_date + " 12:00:00")

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

    def _getWinterCreditEvents(self):
        """Return winter peak events in a more structured way

        :return:

        JSON Object with current_winter, past_winters and next event.
        Current winter have past and future events
        Events have timestamp as key (easier to sort). See Event class for more info

        :example:

            ::

                events = {
                            'current_winter': {
                                'past': { [Event, ...] },
                                'future': { [Event, ...] }
                            },
                            'past_winters': { [Event, ...] },
                            'next': { [Event, ...] }
                        }

        :rtype: dict

        :notes:

        - The next event will be returned only when the current event is completed to avoid interfering with automations
        - The timestamp is the timestamp of the end of the event
        - Future events have a 'pre_heat' datetime as a helper for homeassistant pre-event automations (offset -3h)
        """
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
                    for hydro_event in season['periodesEffacementHiver']:
                        date = parser.isoparse(hydro_event['dateEffacement'])
                        event = Event(
                            config=self.config,
                            date=date,
                            start=self._dateTimeFromString(date.strftime('%Y-%m-%d') + " " + hydro_event['heureDebut']),
                            end=self._dateTimeFromString(date.strftime('%Y-%m-%d') + " " + hydro_event['heureFin'])
                        )

                        future = False
                        if event.end_ts >= self.ref_date.timestamp():
                            future = True
                        if current:
                            if future:
                                events['current_winter']['future'][event.end_ts] = event
                            else:
                                events['current_winter']['past'][event.end_ts] = event
                        else:
                            events['past_winter'][event.end_ts] = event

        next_event = self._getNextEvent(events)
        events['next'] = next_event['next']

        return {'events': events, 'event_in_progress': next_event['event_in_progress']}

    def getFutureEvents(self):
        """Return future events object

        :return: future events list

        :rtype: list
        """
        self._refreshData()
        future_events = []
        for future_ts in self.events['current_winter']['future']:
            future_events.append(self.events['current_winter']['future'][future_ts].to_dict())

        return future_events

    def getAllEvents(self):
        """Return future and past events (Current winter only) object

        :return: events list

        :rtype: list
        """
        self._refreshData()
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
        self._refreshData()
        return self.events['next']

    def _dateTimeFromString(self, date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    def _timestampFromString(self, date_string):
        return self._dateTimeFromString(date_string).timestamp()

    def _getTodayPeakPeriods(self):
        # PEAK PERIODS
        today_peak_morning_start = self._dateTimeFromString(
            self.today_date + " " + self.config.periods.morning_peak_start)
        today_peak_morning_end = self._dateTimeFromString(self.today_date + " " + self.config.periods.morning_peak_end)
        today_peak_evening_start = self._dateTimeFromString(
            self.today_date + " " + self.config.periods.evening_peak_start)
        today_peak_evening_end = self._dateTimeFromString(self.today_date + " " + self.config.periods.evening_peak_end)

        morning = Period(
            config=self.config,
            date=today_peak_morning_start,
            start=today_peak_morning_start,
            end=today_peak_morning_end
        )
        evening = Period(
            config=self.config,
            date=today_peak_evening_start,
            start=today_peak_evening_start,
            end=today_peak_evening_end
        )

        return {'morning': morning, 'evening': evening}

    def _getTodayAnchorPeriods(self, peak_periods, start_offset, duration):
        morning_peak_period = peak_periods['morning']
        evening_peak_period = peak_periods['evening']

        today_anchor_morning_start = morning_peak_period.start_dt - start_offset
        today_anchor_morning_end = today_anchor_morning_start + duration
        today_anchor_evening_start = evening_peak_period.start_dt - start_offset
        today_anchor_evening_end = today_anchor_evening_start + duration

        morning = Period(
            config=self.config,
            date=today_anchor_morning_start,
            start=today_anchor_morning_start,
            end=today_anchor_morning_end
        )
        evening = Period(
            config=self.config,
            date=today_anchor_evening_start,
            start=today_anchor_evening_start,
            end=today_anchor_evening_end
        )

        return {'morning': morning, 'evening': evening}

    def getCurrentState(self):
        """Calculate current periods"""
        self._refreshData()

        peak_periods = self._getTodayPeakPeriods()
        morning_peak_period = peak_periods['morning']
        evening_peak_period = peak_periods['evening']
        anchor_start_offset = datetime.timedelta(hours=self.config.periods.anchor_start_offset)
        anchor_duration = datetime.timedelta(hours=self.config.periods.anchor_duration)
        anchor_periods = self._getTodayAnchorPeriods(peak_periods, anchor_start_offset, anchor_duration)
        morning_anchor_period = anchor_periods['morning']
        evening_anchor_period = anchor_periods['evening']

        '''
        Calculation for the next periods.
        '''
        if self.today.timestamp() <= morning_peak_period.end_ts:
            next_peak_period_start = morning_peak_period.start_dt
            next_peak_period_end = morning_peak_period.end_dt
        elif morning_peak_period.end_ts <= self.today.timestamp() <= evening_peak_period.end_ts:
            next_peak_period_start = evening_peak_period.start_dt
            next_peak_period_end = evening_peak_period.end_dt
        else:
            next_peak_period_start = morning_peak_period.start_dt + datetime.timedelta(days=1)
            next_peak_period_end = morning_peak_period.end_dt + datetime.timedelta(days=1)

        if morning_peak_period.start_ts <= self.today.timestamp() <= morning_peak_period.end_ts:
            current_period = 'peak'
            current_period_time_of_day = 'peak_morning'
        elif evening_peak_period.start_ts <= self.today.timestamp() <= evening_peak_period.end_ts:
            current_period = 'peak'
            current_period_time_of_day = 'peak_evening'
        elif morning_anchor_period.start_ts <= self.today.timestamp() <= morning_anchor_period.end_ts:
            current_period = 'anchor'
            current_period_time_of_day = 'anchor_morning'
        elif evening_anchor_period.start_ts <= self.today.timestamp() <= evening_anchor_period.end_ts:
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
        next_peak_critical = False
        next_event = self.getNextEvent()

        if isinstance(next_event,Event) and next_event.pre_heat_start_ts:
            if next_event.pre_heat_start_ts <= self.today.timestamp() <= next_event.pre_heat_end_ts:
                pre_heat = True
        for event in self.getAllEvents():
            if event.date:
                if event.date == self.today_date:
                    if event.start_ts < self.today_noon_ts:
                        morning_event_today = True
                    else:
                        evening_event_today = True
                    if event.end_ts == next_peak_period_end.timestamp():
                        next_peak_critical = True
                elif event.date == self.tomorrow_date:
                    if event.start_ts < self.tomorrow_noon_ts:
                        morning_event_tomorrow = True
                    else:
                        evening_event_tomorrow = True
                if event.start_ts > self.today.timestamp():
                    upcoming_event = True

        if next_peak_critical:
            current_composite_state = current_period_time_of_day + '_critical'
        else:
            current_composite_state = current_period_time_of_day + '_normal'

        next_peak_period = Period(
            config=self.config,
            date=next_peak_period_start,
            start=next_peak_period_start,
            end=next_peak_period_end,
            critical=next_peak_critical
        )

        next_anchor_period = Period(
            config=self.config,
            date=next_peak_period_start - anchor_start_offset,
            start=next_peak_period_start - anchor_start_offset,
            end=next_peak_period_start - anchor_start_offset + anchor_duration,
            critical=next_peak_critical
        )

        response = {
            'state': {
                'current_period': current_period,
                'current_period_time_of_day': current_period_time_of_day,
                'current_composite_state': current_composite_state,
                'critical': next_peak_critical,
                'event_in_progress': self.event_in_progress,
                'pre_heat': pre_heat,
                'upcoming_event': upcoming_event,
                'morning_event_today': morning_event_today,
                'evening_event_today': evening_event_today,
                'morning_event_tomorrow': morning_event_tomorrow,
                'evening_event_tomorrow': evening_event_tomorrow,
            },
            'next': {
                'peak': next_peak_period.to_dict(),
                'anchor': next_anchor_period.to_dict()
            },
            'anchor_periods': {
                'morning': morning_anchor_period.to_dict(),
                'evening': evening_anchor_period.to_dict()
            },
            'peak_periods': {
                'morning': morning_peak_period.to_dict(),
                'evening': evening_peak_period.to_dict()

            },
            'last_update': self.today.strftime(self.config.formats.datetime_format)
        }
        return response

    def _getCurrentState(self):
        return {}

    def _getPreHeat(self, start):
        """Calculate pre_heat period according to event start date

        :param: start: datetime object representing the start of the next event

        :return: pre_heat period

        :rtype: dict
        """
        print(start)
        pre_heat_start_offset = datetime.timedelta(hours=self.config.periods.pre_heat_start_offset)
        pre_heat_start = start - pre_heat_start_offset
        pre_heat_end_offset = datetime.timedelta(hours=self.config.periods.pre_heat_end_offset)
        pre_heat_end = start - pre_heat_end_offset
        pre_heat = {
            'pre_heat_start': pre_heat_start.strftime(self.config.formats.datetime_format),
            'pre_heat_end': pre_heat_end.strftime(self.config.formats.datetime_format),
            'pre_heat_start_ts': pre_heat_start.timestamp(),
            'pre_heat_end_ts': pre_heat_end.timestamp()
        }
        return pre_heat

    def _getNextEvent(self, events):
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
                event = events['current_winter']['future'][timestamp]
                pre_heat = self._getPreHeat(event.start_dt)
                event.addPreheat(pre_heat['pre_heat_start'], pre_heat['pre_heat_end'],
                                 pre_heat['pre_heat_start_ts'], pre_heat['pre_heat_end_ts'])

                if event.start_ts <= self.ref_date.timestamp() <= event.end_ts:
                    event_in_progress = True
                    next_event_timestamp = timestamp
                    break

            if not event_in_progress:
                next_event_timestamp = min(events['current_winter']['future'], key=float)
        if next_event_timestamp:
            next_event = events['current_winter']['future'][next_event_timestamp]

        return {'next': next_event, 'event_in_progress': event_in_progress}
