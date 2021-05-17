# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
import json

import jmespath

from c7n.exceptions import PolicyValidationError
from c7n.filters.core import Filter
from c7n.filters.core import ValueFilter


class PolicyFilter:
    pass

class OpenstackFilter(Filter):

    def validate(self):
        return self

    def __call__(self, i):
        return self.get_request(i)

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
        print(perm['remote_ip_prefix'])
        found = None
        if perm['description'] == '允许所有':
            return False
        if perm['port_range_min'] is None or perm['port_range_max'] is None :
            return False
        FromPort = int(perm['port_range_min'])
        ToPort = int(perm['port_range_max'])
        for port in self.ports:
            if port >= FromPort and port <= ToPort:
                found = True
                break
            elif FromPort == -1 and ToPort == -1:
                found = True
                break
            else:
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
            found = True
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
        for perm in jmespath.search(self.ip_permissions_key, result):
            perm_matches = {}
            perm_matches['ports'] = self.process_ports(perm)
            perm_matches['cidrs'] = self.process_self_cidrs(perm)
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