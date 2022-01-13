"""Class describing a period"""
import datetime

class Period:
    """This class describe a period object"""
    date = str
    start = str
    end = str
    start_ts = int
    end_ts = int
    critical = bool
    date_dt = datetime.datetime
    start_dt = datetime.datetime
    end_dt = datetime.datetime

    def __init__(self, config, date, start, end, critical = False):
        self.config = config
        self.date_dt = date
        self.start_dt = start
        self.end_dt = end
        self.critical = critical
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
            'critical': self.critical
        }