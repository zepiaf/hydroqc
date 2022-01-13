"""Class describing an event"""
import datetime

class Event:
    """This class describe an event object"""
    date = str
    start = str
    end = str
    start_ts = int
    end_ts = int
    date_dt = datetime.datetime
    start_dt = datetime.datetime
    end_dt = datetime.datetime
    pre_heat_start = ""
    pre_heat_end = ""
    pre_heat_start_ts = int
    pre_heat_end_ts = int

    def __init__(self, config, date, start, end):
        self.config = config
        self.date_dt = date
        self.start_dt = start
        self.end_dt = end
        self.date = date.strftime('%Y-%m-%d')
        self.start = start.strftime(self.config.formats.datetime_format)
        self.end = end.strftime(self.config.formats.datetime_format)
        self.start_ts = self.start_dt.timestamp()
        self.end_ts = self.end_dt.timestamp()

    def __dict__(self):
        return {
            'date': self.date,
            'start': self.start,
            'end': self.end,
            'start_ts': self.start_ts,
            'end_ts': self.end_ts,
            'pre_heat_start': self.pre_heat_start,
            'pre_heat_end': self.pre_heat_end
        }

    def addPreheat(self,start, end, start_ts, end_ts):
        self.pre_heat_start = start
        self.pre_heat_end = end
        self.pre_heat_start_ts = start_ts
        self.pre_heat_end_ts = end_ts

