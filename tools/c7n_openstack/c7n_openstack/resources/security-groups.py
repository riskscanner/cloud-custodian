# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import jmespath

from c7n.utils import type_schema
from c7n_openstack.filters.filter import SGPermission
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo
from c7n_openstack.filters.filter import SGPermissionSchema, OpenstackFilter


@resources.register('security-groups')
class SecurityGroups(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_security_groups', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name']

@SecurityGroups.filter_registry.register('ingress')
class IPIngressPermission(SGPermission):
    """Filters SecurityGroups based on their system
    :example:
    .. code-block:: yaml
            policies:
              # 扫描开放以下高危端口的安全组：
              - name: openstack-security-groups
                resource: openstack.security-groups
                filters:
                  - or:
                    - type: ingress
                      IpProtocol: "-1"
                      Ports: [20,21,22,25,80,773,765, 1733,1737,3306,3389,7333,5732,5500]
                      Cidr: "0.0.0.0/0"
                    - type: ingress
                      IpProtocol: "-1"
                      Ports: [20,21,22,25,80,773,765, 1733,1737,3306,3389,7333,5732,5500]
                      CidrV6: "::/0"
    """
    ip_permissions_key = "security_group_rules"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['ingress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def process_self_cidrs(self, perm):
        return self.process_cidrs(perm, 'remote_ip_prefix', 'remote_ip_prefix')

    def securityGroupAttributeRequst(self, sg):
        self.direction = 'Ingress'
        return sg

@SecurityGroups.filter_registry.register('egress')
class IPEgressPermission(SGPermission):
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['egress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def securityGroupAttributeRequst(self, sg):
        self.direction = 'Egress'
        return sg

@SecurityGroups.filter_registry.register('source-cidr-ip')
class SourceCidrIp(OpenstackFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下安全组配置不为“0.0.0.0/0”，视为“合规”。
            - name: openstack-sg-source-cidr-ip
              resource: openstack.security-groups
              filters:
                - type: source-cidr-ip
                  value: "0.0.0.0/0"
    """

    ip_permissions_key = "security_group_rules"
    schema = type_schema(
        'source-cidr-ip',
        **{'value': {'type': 'string'}})

    def get_request(self, sg):
        for cidr in jmespath.search(self.ip_permissions_key, sg):
            if cidr['remote_ip_prefix'] == self.data['value']:
                return sg
        return False
