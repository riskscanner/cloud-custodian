# Copyright 2017-2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import jmespath
import urllib3
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkvpc.v2 import *

from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import SGPermission, HuaweiSgFilter
from c7n_huawei.filters.filter import SGPermissionSchema
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'security-group'

@resources.register('security-group')
class SecurityGroup(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'security-group'
        enum_spec = (None, 'security_groups', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListSecurityGroupsRequest()
            response = Session.client(self, service).list_security_groups(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@SecurityGroup.filter_registry.register('ingress')
class IPPermission(SGPermission):

    """
        policies:
            #扫描开放以下高危端口的安全组：
            #(20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500)
            - name: huawei-security-group
              resource: huawei.security-group
              description: |
                    Add Filter all security groups, filter ports
                    [20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500]
                    on 0.0.0.0/0 or
                    [20,21,22,25,80,443,465, 1433,1434,3306,3389,4333,5432,5500]
                    on ::/0 (IPv6)
              filters:
                  - or:
                      - type: ingress
                        IpProtocol: tcp
                        Ports: [20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500]
                        Cidr: "0.0.0.0/0"
                      - type: ingress
                        IpProtocol: tcp
                        Ports: [20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500]
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
        return self.process_cidrs(perm, "remote_ip_prefix", "remote_ip_prefix")


    def securityGroupAttributeRequst(self, sg):
        self.direction = 'ingress'
        return sg

@SecurityGroup.filter_registry.register('egress')
class IPPermission(SGPermission):
    ip_permissions_key = "security_group_rules"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['egress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def securityGroupAttributeRequst(self, sg):
        self.direction = 'egress'
        return sg

    def process_self_cidrs(self, perm):
        return self.process_cidrs(perm, "DestCidrIp", "Ipv6DestCidrIp")

@SecurityGroup.filter_registry.register('source-cidr-ip')
class HuaweiSgSourceCidrIp(HuaweiSgFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下ECS安全组配置不为“0.0.0.0/0”，视为“合规”。
            - name: huawei-sg-source-cidr-ip
              resource: huawei.security-group
              filters:
                - type: source-cidr-ip
                  value: "0.0.0.0/0"
    """

    ip_permissions_key = "security_group_rules"
    schema = type_schema(
        'source-cidr-ip',
        **{'value': {'type': 'string'}})

    def get_request(self, sg):
        for cidr in sg[self.ip_permissions_key]:
            if cidr['remote_ip_prefix'] is not None and cidr['remote_ip_prefix'] == self.data['value']:
                return sg
        return False