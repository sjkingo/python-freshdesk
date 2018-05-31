import dateutil.parser


class FreshdeskModel(object):
    _keys = set()

    def __init__(self, **kwargs):
        if "custom_field" in kwargs.keys() and len(kwargs["custom_field"]) > 0:
            custom_fields = kwargs.pop("custom_field")
            kwargs.update(custom_fields)
        for k, v in kwargs.items():
            if hasattr(Ticket, k):
                k = '_' + k
            setattr(self, k, v)
            self._keys.add(k)
        self.created_at = self._to_timestamp(self.created_at)
        self.updated_at = self._to_timestamp(self.updated_at)

    def _to_timestamp(self, timestamp_str):
        """Converts a timestamp string as returned by the API to
        a native datetime object and return it."""
        return dateutil.parser.parse(timestamp_str)


class Ticket(FreshdeskModel):
    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Ticket \'{}\' #{}>'.format(self.subject, self.id)

    @property
    def priority(self):
        _p = {1: 'low', 2: 'medium', 3: 'high', 4: 'urgent'}
        return _p[self._priority]

    @property
    def status(self):
        _s = {2: 'open', 3: 'pending', 4: 'resolved', 5: 'closed'}
        try:
            return _s[self._status]
        except KeyError:
            return 'status_{}'.format(self._status)

    @property
    def source(self):
        _s = {1: 'email', 2: 'portal', 3: 'phone', 4: 'forum', 5: 'twitter',
              6: 'facebook', 7: 'chat'}
        return _s[self._source]


class Group(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Group \'{}\'>'.format(self.name)


class Comment(FreshdeskModel):
    def __str__(self):
        return self.body_text

    def __repr__(self):
        return '<Comment for Ticket #{}>'.format(self.ticket_id)

    @property
    def source(self):
        _s = {0: 'reply', 2: 'note', 5: 'twitter', 6: 'survey', 7: 'facebook',
              8: 'email', 9: 'phone', 10: 'mobihelp', 11: 'e-commerce'}
        return _s[self._source]


class Contact(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Contact \'{}\'>'.format(self.name)


class TimeEntry(FreshdeskModel):
    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<Timesheet Entry {}>'.format(self.id)


class Customer(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Customer \'{}\'>'.format(self.name)

class Company(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Company \'{}\>'.format(self.name)

class Agent(FreshdeskModel):
    def __str__(self):
        return self.contact.name

    def __repr__(self):
        return '<Agent \'{}\'>'.format(self.contact.name)    


class Role(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Role\'{}\'>'.format(self.name)    

