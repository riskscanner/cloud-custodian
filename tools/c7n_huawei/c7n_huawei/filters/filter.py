import datetime
from concurrent.futures import as_completed
from datetime import timedelta

from dateutil.parser import parse
from dateutil.tz import tzutc
from openstack import utils

from c7n.exceptions import PolicyValidationError
from c7n.filters.core import Filter
from c7n.filters.core import OPERATORS
from c7n.filters.core import ValueFilter
from c7n.utils import local_session, chunks
from c7n.utils import type_schema


class HuaweiEcsFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiEipFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiDiskFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiElbFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiVpcFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiSgFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiIamFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiRedisFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class HuaweiRdsFilter(Filter):
        schema = None

        def validate(self):
            return self

        def __call__(self, i):
            return self.get_request(i)

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
        # Work around placebo issues with tz
        utc_date = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
        v = utc_date + datetime.timedelta(hours=8)
        op = OPERATORS[self.data.get('op', 'greater-than')]

        if not self.threshold_date:

            days = self.data.get('days', 0)
            hours = self.data.get('hours', 0)
            minutes = self.data.get('minutes', 0)

            n = datetime.datetime.now()
            self.threshold_date = n - timedelta(days=days, hours=hours, minutes=minutes)

        return op(self.threshold_date, v)

class SGPermission(Filter):
    """Filter for verifying security group ingress and egress permissions

    All attributes of a security group permission are available as
    value filters.

    If multiple attributes are specified the permission must satisfy
    all of them. Note that within an attribute match against a list value
    of a permission we default to or.

    If a group has any permissions that match all conditions, then it
    matches the filter.

    Permissions that match on the group are annotated onto the group and
    can subsequently be used by the remove-permission action.

    We have specialized handling for matching `Ports` in ingress/egress
    permission From/To range. The following example matches on ingress
    rules which allow for a range that includes all of the given ports.

    .. code-block:: yaml

      - type: ingress
        Ports: [22, 443, 80]

    As well for verifying that a rule only allows for a specific set of ports
    as in the following example. The delta between this and the previous
    example is that if the permission allows for any ports not specified here,
    then the rule will match. ie. OnlyPorts is a negative assertion match,
    it matches when a permission includes ports outside of the specified set.

    .. code-block:: yaml

      - type: ingress
        OnlyPorts: [22]

    For simplifying ipranges handling which is specified as a list on a rule
    we provide a `Cidr` key which can be used as a value type filter evaluated
    against each of the rules. If any iprange cidr match then the permission
    matches.

    .. code-block:: yaml

      - type: ingress
        IpProtocol: -1
        FromPort: 445

    We also have specialized handling for matching self-references in
    ingress/egress permissions. The following example matches on ingress
    rules which allow traffic its own same security group.

    .. code-block:: yaml

      - type: ingress
        SelfReference: True

    As well for assertions that a ingress/egress permission only matches
    a given set of ports, *note* OnlyPorts is an inverse match.

    .. code-block:: yaml

      - type: egress
        OnlyPorts: [22, 443, 80]

      - type: egress
        Cidr:
          value_type: cidr
          op: in
          value: x.y.z

    `Cidr` can match ipv4 rules and `CidrV6` can match ipv6 rules.  In
    this example we are blocking global inbound connections to SSH or
    RDP.

    .. code-block:: yaml

      - type: ingress
        Ports: [22, 3389]
        Cidr:
          value:
            - "0.0.0.0/0"
            - "::/0"
          op: in

    `SGReferences` can be used to filter out SG references in rules.
    In this example we want to block ingress rules that reference a SG
    that is tagged with `Access: Public`.

    .. code-block:: yaml

      - type: ingress
        SGReferences:
          key: "tag:Access"
          value: "Public"
          op: equal

    We can also filter SG references based on the VPC that they are
    within. In this example we want to ensure that our outbound rules
    that reference SGs are only referencing security groups within a
    specified VPC.

    .. code-block:: yaml

      - type: egress
        SGReferences:
          key: 'VpcId'
          value: 'vpc-11a1a1aa'
          op: equal

    Likewise, we can also filter SG references by their description.
    For example, we can prevent egress rules from referencing any
    SGs that have a description of "default - DO NOT USE".

    .. code-block:: yaml

      - type: egress
        SGReferences:
          key: 'Description'
          value: 'default - DO NOT USE'
          op: equal

    """

    perm_attrs = {
        'IpProtocol', "Priority", 'Policy'}
    filter_attrs = {
        'Cidr', 'CidrV6', 'Ports', 'OnlyPorts',
        'SelfReference', 'Description', 'SGReferences'}
    attrs = perm_attrs.union(filter_attrs)
    attrs.add('match-operator')
    attrs.add('match-operator')

    def validate(self):
        delta = set(self.data.keys()).difference(self.attrs)
        delta.remove('type')
        if delta:
            raise PolicyValidationError("Unknown keys %s on %s" % (
                ", ".join(delta), self.manager.data))
        return self

    def process(self, resources, event=None):
        self.vfilters = []
        fattrs = list(sorted(self.perm_attrs.intersection(self.data.keys())))
        self.ports = 'Ports' in self.data and self.data['Ports'] or ()
        self.only_ports = (
            'OnlyPorts' in self.data and self.data['OnlyPorts'] or ())
        for f in fattrs:
            fv = self.data.get(f)
            if isinstance(fv, dict):
                fv['key'] = f
            else:
                fv = {f: fv}
            vf = ValueFilter(fv, self.manager)
            vf.annotate = False

            self.vfilters.append(vf)

        return super(SGPermission, self).process(resources, event)

    def process_ports(self, perm):
        found = None
        if perm['port_range_max'] is not None and perm['port_range_min'] is not None:
            FromPort = int(perm['port_range_max'])
            ToPort = int(perm['port_range_min'])
            for port in self.ports:
                if port >= FromPort and port <= ToPort:
                    return True
                found = False
            only_found = False
            for port in self.only_ports:
                if port == FromPort and port == ToPort:
                    only_found = True
            if self.only_ports and not only_found:
                found = found is None or found and True or False
            if self.only_ports and only_found:
                found = False
        return found


    def _process_cidr(self, cidr_key, cidr_type, SourceCidrIp, perm):
        found = None
        SourceCidrIp = perm.get(SourceCidrIp, "")
        if not SourceCidrIp:
            return False
        SourceCidrIp = {cidr_type: SourceCidrIp}
        match_range = self.data[cidr_key]
        if isinstance(match_range, dict):
            match_range['key'] = cidr_type
        else:
            match_range = {cidr_type: match_range}
        vf = ValueFilter(match_range, self.manager)
        vf.annotate = False
        found = vf(SourceCidrIp)
        if found:
            pass
        else:
            found = False
        return found

    def process_cidrs(self, perm, ipv4Cidr, ipv6Cidr):
        found_v6 = found_v4 = None
        if 'CidrV6' in self.data:
            found_v6 = self._process_cidr('CidrV6', 'CidrIpv6', ipv6Cidr, perm)
        if 'Cidr' in self.data:
            found_v4 = self._process_cidr('Cidr', 'CidrIp', ipv4Cidr, perm)
        match_op = self.data.get('match-operator', 'and') == 'and' and all or any
        cidr_match = [k for k in (found_v6, found_v4) if k is not None]
        if not cidr_match:
            return None
        return match_op(cidr_match)

    def process_description(self, perm):
        if 'Description' not in self.data:
            return None

        d = dict(self.data['Description'])
        d['key'] = 'Description'

        vf = ValueFilter(d, self.manager)
        vf.annotate = False

        for k in ('Ipv6Ranges', 'IpRanges', 'UserIdGroupPairs', 'PrefixListIds'):
            if k not in perm or not perm[k]:
                continue
            return vf(perm[k][0])
        return False

    def process_self_reference(self, perm, sg_id):
        found = None
        ref_match = self.data.get('SelfReference')
        if ref_match is not None:
            found = False
        if 'UserIdGroupPairs' in perm and 'SelfReference' in self.data:
            self_reference = sg_id in [p['GroupId']
                                       for p in perm['UserIdGroupPairs']]
            if ref_match is False and not self_reference:
                found = True
            if ref_match is True and self_reference:
                found = True
        return found

    def process_sg_references(self, perm, owner_id):
        sg_refs = self.data.get('SGReferences')
        if not sg_refs:
            return None

        sg_perm = perm.get('UserIdGroupPairs', [])
        if not sg_perm:
            return False

        sg_group_ids = [p['GroupId'] for p in sg_perm if p['UserId'] == owner_id]
        sg_resources = self.manager.get_resources(sg_group_ids)
        vf = ValueFilter(sg_refs, self.manager)
        vf.annotate = False

        for sg in sg_resources:
            if vf(sg):
                return True
        return False

    def __call__(self, resource):
        result = self.securityGroupAttributeRequst(resource)
        matched = []
        match_op = self.data.get('match-operator', 'and') == 'and' and all or any
        for perm in result[self.ip_permissions_key]:
            if perm['direction'] != self.direction:
                continue
            perm_matches = {}
            perm_matches['cidrs'] = self.process_self_cidrs(perm)
            perm_matches['ports'] = self.process_ports(perm)
            perm_match_values = list(filter(
                lambda x: x is not None, perm_matches.values()))
            # account for one python behavior any([]) == False, all([]) == True
            if match_op == all and not perm_match_values:
                continue

            match = match_op(perm_match_values)
            if match:
                matched.append(perm)
        if matched:
            resource['Matched%s' % self.ip_permissions_key] = matched
            return True

class MetricsFilter(Filter):
    """Supports   metrics filters on resources.
    .. code-block:: yaml

      - name: ecs-underutilized
        resource: ecs
        filters:
          - type: metrics
            name: CPUUtilization
            days: 4
            period: 86400
            value: 30
            op: less-than

    Note periods when a resource is not sending metrics are not part
    of calculated statistics as in the case of a stopped ecs instance,
    nor for resources to new to have existed the entire
    period. ie. being stopped for an ecs instance wouldn't lower the
    average cpu utilization.

    The "missing-value" key allows a policy to specify a default
    value when CloudWatch has no data to report:

    .. code-block:: yaml

      - name: elb-low-request-count
        resource: elb
        filters:
          - type: metrics
            name: RequestCount
            statistics: Sum
            days: 7
            value: 7
            missing-value: 0
            op: less-than

    This policy matches any ELB with fewer than 7 requests for the past week.
    ELBs with no requests during that time will have an empty set of metrics.
    Rather than skipping those resources, "missing-value: 0" causes the
    policy to treat their request counts as 0.

    Note the default statistic for metrics is Average.
    """

    schema = type_schema(
        'metrics',
        **{'namespace': {'type': 'string'},
           'name': {'type': 'string'},
           'dimensions': {
               'type': 'object',
               'patternProperties': {
                   '^.*$': {'type': 'string'}}},
           # Type choices
           'statistics': {'type': 'string', 'enum': [
               'average', 'sum', 'maximum', 'minimum', 'samplecount']},
           'days': {'type': 'number'},
           'op': {'type': 'string', 'enum': list(OPERATORS.keys())},
           'value': {'type': 'number'},
           'period': {'type': 'number'},
           'attr-multiplier': {'type': 'number'},
           'percent-attr': {'type': 'string'},
           'missing-value': {'type': 'number'},
           'required': ('value', 'name')})
    schema_alias = True

    MAX_QUERY_POINTS = 50850
    MAX_RESULT_POINTS = 1440

    # Default per service, for overloaded services like ecs
    # we do type specific default namespace annotation
    # specifically AWS/EBS and AWS/ecsSpot

    # ditto for spot fleet
    DEFAULT_NAMESPACE = {
        'ecs': 'SYS.ECS',
        'rds': 'SYS.RDS'
    }

    DEFAULT_METRIC = {
        'rds_mem_util': 'rds002_mem_util',
        'rds_iops': 'rds003_iops',
        'cpu_util': 'cpu_util',
        'mem_util': 'mem_util'
    }

    def process(self, resources, event=None):
        now = datetime.datetime.now()
        days = self.data.get('days', 1)
        duration = timedelta(days)
        ago = now - duration
        if self.data['name'] in self.DEFAULT_METRIC:
            self.metric = self.DEFAULT_METRIC[self.data['name']]
        else:
            self.metric = self.data['name']
        self.end = utils.get_epoch_time(now)
        self.start = utils.get_epoch_time(ago)
        self.period = int(self.data.get('period', duration.total_seconds()))
        self.statistics = self.data.get('statistics', 'average')
        self.model = self.manager.get_model()
        self.op = OPERATORS[self.data.get('op', 'less-than')]
        self.value = self.data['value']
        self.namespace = self.DEFAULT_NAMESPACE[self.model.service]
        self.log.debug("Querying metrics for %d", len(resources))
        matched = []
        with self.executor_factory(max_workers=3) as w:
            futures = []
            for resource_set in chunks(resources, 50):
                futures.append(
                    w.submit(self.process_resource_set, resource_set))

            for f in as_completed(futures):
                if f.exception():
                    self.log.warning(
                        "CW Retrieval error: %s" % f.exception())
                    continue
                matched.extend(f.result())
        return matched

    def get_dimensions(self, resource):
        return [{self.model.dimension: resource[self.model.dimension]}]

    def get_user_dimensions(self):
        dims = []
        if 'dimensions' not in self.data:
            return dims
        for k, v in self.data['dimensions'].items():
            dims.append({'Name': k, 'Value': v})
        return dims

    def process_resource_set(self, resource_set):
        client = local_session(
            self.manager.session_factory).client(self.manager.get_model().service)

        matched = []
        for r in resource_set:
            # if we overload dimensions with multiple resources we get
            # the statistics/average over those resources.
            dimensions = self.get_dimensions(r)
            # Merge in any filter specified metrics, get_dimensions is
            # commonly overridden so we can't do it there.
            # dimensions.extend(self.get_user_dimensions())

            request = self.get_request(dimensions)
            collected_metrics = r.setdefault('c7n_huawei.metrics', {})
            # Note this annotation cache is policy scoped, not across
            # policies, still the lack of full qualification on the key
            # means multiple filters within a policy using the same metric
            # across different periods or dimensions would be problematic.
            key = "%s.%s.%s" % (self.namespace, self.metric, self.statistics)
            if key not in collected_metrics:
                collected_metrics[key] = request.metrics

            # In certain cases CloudWatch reports no data for a metric.
            # If the policy specifies a fill value for missing data, add
            # that here before testing for matches. Otherwise, skip
            # matching entirely.
            # for m in collected_metrics[key]:
            if len(collected_metrics[key]) == 0:
                if 'missing-value' not in self.data:
                    continue
                collected_metrics[key].append({'timestamp': self.start, self.statistics: self.data['missing-value'], 'c7n_huawei:detail': 'Fill value for missing data'})
            if self.data.get('percent-attr'):
                rvalue = r[self.data.get('percent-attr')]
                if self.data.get('attr-multiplier'):
                    rvalue = rvalue * self.data['attr-multiplier']
                percent = (collected_metrics[key][0].datapoints[0][self.statistics] /
                           rvalue * 100)
                if self.op(percent, self.value):
                    matched.append(r)
            else:
                datapoints = collected_metrics[key][0].datapoints
                if len(datapoints) > 0:
                    for data in datapoints:
                        if self.op(data[self.statistics], self.value):
                            matched.append(r)
        return matched

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
