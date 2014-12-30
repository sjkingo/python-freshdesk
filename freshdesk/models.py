
class Ticket(object):
    _keys = set()

    def __init__(self, **kwargs):
        for k,v  in kwargs.items():
            setattr(self, k, v)
            self._keys.add(k)

    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Ticket \'{}\'>'.format(self.subject)
