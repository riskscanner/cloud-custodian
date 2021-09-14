import datetime
import json
import re
from concurrent.futures import as_completed
from datetime import timedelta

import jmespath
from dateutil.parser import parse
from dateutil.tz import tzutc

from c7n.exceptions import PolicyValidationError
from c7n.filters.core import Filter
from c7n.filters.core import OPERATORS
from c7n.filters.core import ValueFilter
from c7n.utils import local_session, chunks
from c7n.utils import type_schema


class TencentFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class TencentEipFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        if i['AddressStatus'] != self.data['type']:
            return False
        return i

class TencentDiskFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        if i['DiskState'] != self.data['type']:
            return False
        return i

class TencentCdbFilter(Filter):
    schema = None

    def validate(self):
        return self

    def __call__(self, i):
        Internet = 0
        if self.data['type'] == 'Internet':
            Internet = 1
        if i['WanStatus'] != Internet:
            return False
        return i

class TencentClbFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class TencentVpcFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

class TencentAgeFilter(Filter):
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
        utc_date = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
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
        'Cidr', 'CidrV6', 'Ports', 'OnlyPorts', 'Action',
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
        found = False
        if self.ip_permissions_type == 'ingress':
            poms = perm['IpPermissions']['Ingress']
        else:
            poms = perm['IpPermissions']['Egress']
        for ingress in poms:
            if ingress['Action'] != 'ACCEPT':
                found = False
            if ingress['Port']:
                FromPort = ingress['Port']
                for port in self.ports:
                    if FromPort == "ALL":
                        found = True
                        break
                    else:
                        if ',' in FromPort:
                            strs = FromPort.split(',')
                            for str in strs:
                                if port == int(str):
                                    return True
                        elif '-' in FromPort:
                            strs = FromPort.split('-')
                            p1 = int(strs[0])
                            p2 = int(strs[1])
                            if port >= p1 and port <= p2:
                                return True
                        else:
                            if port == int(FromPort):
                                return True
                    found = False
                only_found = False
                for port in self.only_ports:
                    if port == FromPort:
                        only_found = True
                if self.only_ports and not only_found:
                    found = found is False or found and True or False
                if self.only_ports and only_found:
                    found = False
            if found:
                return found
        return found

    def cidr_process_ports(self, poms):
        found = False
        for pom in poms:
            if pom['Action'] != 'ACCEPT':
                found = False
            if pom['Port']:
                FromPort = pom['Port']
                for port in self.ports:
                    if FromPort == "ALL":
                        return True
                    else:
                        if ',' in FromPort:
                            strs = FromPort.split(',')
                            for str in strs:
                                if port == int(str):
                                    return True
                        elif '-' in FromPort:
                            strs = FromPort.split('-')
                            p1 = int(strs[0])
                            p2 = int(strs[1])
                            if port >= p1 and port <= p2:
                                return True
                        else:
                            if port == int(FromPort):
                                return True
                    found = False
                only_found = False
                for port in self.only_ports:
                    if port == FromPort:
                        only_found = True
                if self.only_ports and not only_found:
                    found = found is False or found and True or False
                if self.only_ports and only_found:
                    found = False
        return found

    def _process_cidr(self, cidr_key, cidr_type, cidr, perm):
        found = False
        if not cidr:
            return False
        action = self.data.get('Action', '')
        if self.ip_permissions_type == 'ingress':
            items = perm.get('IpPermissions', {}).get('Ingress', [])
        else:
            items = perm.get('IpPermissions', {}).get('Egress', [])
        for ip_Permission in items:
            ip_action = ip_Permission.get('Action', '')
            if action == ip_action:
                found = True
            else:
                found = False
                continue
            #0.0.0.0/0
            CidrBlock = ip_Permission.get(cidr, "")
            if CidrBlock == self.data.get(cidr_key, ""):
                found = True
            else:
                found = False
                continue
            IpProtocol = self.data.get('IpProtocol', "").upper()
            if IpProtocol in ["-1", -1]:
                IpProtocol = "ALL"
            outProtocol = ip_Permission.get("Protocol", "").upper()
            if outProtocol=="ALL" or IpProtocol == "ALL":
                found = True
            else:
                if IpProtocol == outProtocol:
                    found = True
                else:
                    found = False
                    continue
            if found:
                break
        if found:
            found = self.cidr_process_ports(items)
        return found

    def process_cidrs(self, perm, CidrBlock, Ipv6CidrBlock):
        found_v6 = found_v4 = False
        if 'CidrV6' in self.data:
            found_v6 = self._process_cidr('CidrV6', 'CidrIpv6', Ipv6CidrBlock, perm)
        if 'Cidr' in self.data:
            found_v4 = self._process_cidr('Cidr', 'CidrIp', CidrBlock, perm)
        match_op = self.data.get('match-operator', 'and') == 'and' and all or any
        cidr_match = [k for k in (found_v6, found_v4) if k is not False]
        if not cidr_match:
            return False
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
            return False

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
        perm = self.securityGroupAttributeRequst(resource)
        matched = []
        match_op = self.data.get('match-operator', 'and') == 'and' and all or any
        if len(perm.get('IpPermissions', {}).get(self.direction, [])) == 0:
            return False
        # result = self.securityGroupAttributeRequst(resource)
        # matched = []
        # match_op = self.data.get('match-operator', 'and') == 'and' and all or any
        # for perm in jmespath.search(self.ip_permissions_key, json.loads(result)):
        #     if perm.get('IpPermissions') is None or len(perm.get('IpPermissions', {}).get(self.direction, [])) == 0:
        #         continue
        perm_matches = {}
        # 将cidrs和ports合并，关联判断
        perm_matches['cidrs'] = self.process_self_cidrs(perm)
        return perm_matches['cidrs']
        # perm_matches['ports'] = self.process_ports(perm)
        # perm_match_values = list(filter(
        #     lambda x: x is not None, perm_matches.values()))
        # # account for one python behavior any([]) == False, all([]) == True
        # if match_op == all and not perm_match_values:
        #     return False
        # match = match_op(perm_match_values)
        # if match:
        #     matched.append(perm)
        #
        # if matched:
        #     resource['Matched%s' % self.ip_permissions_key] = matched
        #     return True

class MetricsFilter(Filter):
    """Supports   metrics filters on resources.
    .. code-block:: yaml

      - name: tencent-cvm-underutilized
        resource: tencent.cvm
        filters:
          - type: metrics
            name: CPUUsage
            days: 4
            period: 86400
            value: 30
            op: less-than

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
               'Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']},
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
        'cvm': 'CPUUsage',
    }

    def process(self, resources, event=None):
        days = self.data.get('days', 1)
        duration = timedelta(days)
        self.metric = self.data['name']
        self.end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.start = (datetime.datetime.now() - duration).strftime("%Y-%m-%d %H:%M:%S")
        self.period = int(self.data.get('period', duration.total_seconds()))
        self.statistics = self.data.get('statistics', 'Average')
        self.model = self.manager.get_model()
        self.op = OPERATORS[self.data.get('op', 'less-than')]
        self.value = self.data.get('value', '')
        self.namespace = self.model.namespace
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
                        "CW Retrieval error(): %s" % f.exception())
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
        service = []
        service.append("monitor_client")
        client = local_session(
            self.manager.session_factory).client(service)

        matched = []
        for r in resource_set:
            request = self.get_request()

            instance = '{"Name": "' + self.model.dimension + '", "Value": "' + r[self.model.dimension] + '"}'
            Dimensions = '[{"Dimensions": [' + instance + ']}]'
            params = '{"Namespace": "QCE/CVM", "MetricName": "' + self.metric + '", "Instances": ' + Dimensions + '}'
            request.from_json_string(params)
            resp = client.GetMonitorData(request)
            reponse = resp.to_json_string()

            collected_metrics = r.setdefault('c7n_tencent.metrics', {})
            key = "%s.%s.%s" % (self.namespace, self.metric, self.statistics)
            if key not in collected_metrics:

                collected_metrics[key] = json.loads(reponse)["DataPoints"]
            if len(collected_metrics[key]) == 0:
                if 'missing-value' not in self.data:
                    continue
                collected_metrics[key].append({'timestamp': self.start, self.statistics: self.data['missing-value'], 'c7n_tencent:detail': 'Fill value for missing data'})
            if self.data.get('percent-attr', None) != None:
                rvalue = r[self.data.get('percent-attr')]
                if self.data.get('attr-multiplier'):
                    rvalue = rvalue * self.data['attr-multiplier']
                percent = (collected_metrics[key][0]['Values'][0] /
                           rvalue * 100)
                if self.op(percent, self.value):
                    matched.append(r)
            elif self.op(collected_metrics[key][0]['Values'][0], self.value):
                matched.append(r)
        return matched

SGPermissionSchema = {
    'match-operator': {'type': 'string', 'enum': ['or', 'and']},
    'Ports': {'type': 'array', 'items': {'type': 'integer'}},
    'OnlyPorts': {'type': 'array', 'items': {'type': 'integer'}},
    'Policy': {},
    'IpProtocol': {
        'oneOf': [
            {'enum': ["-1", -1, 'TCP', 'UDP', 'ICMP', 'ICMPV6', 'tcp', 'udp', 'icmp', 'icmpv6']},
            {'$ref': '#/definitions/filters/value'}
        ]
    },
    'Action':  {'type': 'string', 'enum': ['ACCEPT', 'DROP']},
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
