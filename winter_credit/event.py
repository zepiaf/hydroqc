"""Class describing an event"""

class Event:
    """This class describe an event object"""

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
        self.pre_heat_start = None
        self.pre_heat_end = None
        self.pre_heat_start_ts = None
        self.pre_heat_end_ts = None

    def to_dict(self):
        if self.pre_heat_start:
            return {
                'date': self.date,
                'start': self.start,
                'end': self.end,
                'start_ts': self.start_ts,
                'end_ts': self.end_ts,
                'pre_heat_start': self.pre_heat_start,
                'pre_heat_end': self.pre_heat_end,
                'pre_heat_start_ts': self.pre_heat_start_ts,
                'pre_heat_end_ts': self.pre_heat_end_ts
            }
        else:
            return {
                'date': self.date,
                'start': self.start,
                'end': self.end,
                'start_ts': self.start_ts,
                'end_ts': self.end_ts,
            }


    def addPreheat(self,start, end, start_ts, end_ts):
        self.pre_heat_start = start
        self.pre_heat_end = end
        self.pre_heat_start_ts = start_ts
        self.pre_heat_end_ts = end_ts

