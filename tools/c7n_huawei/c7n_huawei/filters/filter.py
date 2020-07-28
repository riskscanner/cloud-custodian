import datetime
from datetime import timedelta

from dateutil.parser import parse
from dateutil.tz import tzutc

from c7n.filters.core import Filter
from c7n.filters.core import OPERATORS


class HuaweiAgeFilter(Filter):
    """Automatically filter resources older than a given date.

    **Deprecated** use a value filter with `value_type: age` which can be
    done on any attribute.
    """
    threshold_date = None

    schema = None

    def validate(self):
        return self

    def get_resource_date(self, i):
        v = i[self.date_attribute]
        if not isinstance(v, datetime.datetime):
            v = parse(v)
        if not v.tzinfo:
            v = v.replace(tzinfo=tzutc())
        return v

    def __call__(self, i):
        v = self.get_resource_date(i)
        if v is None:
            return False
        op = OPERATORS[self.data.get('op', 'greater-than')]
        if not self.threshold_date:
            days = self.data.get('days', 0)
            hours = self.data.get('hours', 0)
            minutes = self.data.get('minutes', 0)
            # Work around placebo issues with tz
            utc_date = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
            v = utc_date + datetime.timedelta(hours=8)
            n = datetime.datetime.now()
            self.threshold_date = n - timedelta(days=days, hours=hours, minutes=minutes)

        return op(self.threshold_date, v)

SGPermissionSchema = {
    'match-operator': {'type': 'string', 'enum': ['or', 'and']},
    'Ports': {'type': 'array', 'items': {'type': 'integer'}},
    'OnlyPorts': {'type': 'array', 'items': {'type': 'integer'}},
    'Policy': {},
    'IpProtocol': {
        'oneOf': [
            {'enum': ["-1", -1, 'TCP', 'UDP', 'ICMP', 'ICMPV6']},
            {'$ref': '#/definitions/filters/value'}
        ]
    },
    'FromPort': {'oneOf': [
        {'$ref': '#/definitions/filters/value'},
        {'type': 'integer'}]},
    'ToPort': {'oneOf': [
        {'$ref': '#/definitions/filters/value'},
        {'type': 'integer'}]},
    'IpRanges': {},
    'Cidr': {},
    'CidrV6': {},
    'SGReferences': {}
}
