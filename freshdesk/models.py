import datetime

class Ticket(object):
    _keys = set()

    def __init__(self, **kwargs):
        for k,v  in kwargs.items():
            setattr(self, k, v)
            self._keys.add(k)
        self.created_at = self._to_timestamp(self.created_at)
        self.updated_at = self._to_timestamp(self.updated_at)

    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Ticket \'{}\'>'.format(self.subject)

    def _to_timestamp(self, timestamp_str):
        """Converts a timestamp string as returned by the API to
        a native datetime object and return it."""
        return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S+10:00')
