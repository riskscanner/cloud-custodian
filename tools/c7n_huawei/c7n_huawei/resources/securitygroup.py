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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import SGPermission
from c7n_huawei.filters.filter import SGPermissionSchema
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'network.security-group'

@resources.register('security-group')
class SecurityGroup(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'network.security-group'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        query = {
            "limit": 10000
        }
        sgs = Session.client(self, service).security_groups(**query)
        arr = list() # 创建 []
        if sgs is not None:
            for sg in sgs:
                json = dict() # 创建 {}
                for name in dir(sg):
                    if not name.startswith('_'):
                        value = getattr(sg, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr

@SecurityGroup.action_registry.register('delete')
class Delete(MethodAction):

    """
        policies:
          - name: huawei-security-group-delete
            resource: huawei.security-group
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, security_group):
        obj = Session.client(self, service).delete_security_group(security_group['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json

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
        self.process_cidrs(perm, "remote_ip_prefix", "remote_ip_prefix")


    def securityGroupAttributeRequst(self, sg):
        obj = Session.client(self, service).find_security_group(sg['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json

@SecurityGroup.filter_registry.register('egress')
class IPPermission(SGPermission):
    ip_permissions_key = "Permissions.Permission"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['egress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def securityGroupAttributeRequst(self, sg):
        obj = Session.client(self, service).find_security_group(sg['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json

    def process_self_cidrs(self, perm):
        self.process_cidrs(perm, "DestCidrIp", "Ipv6DestCidrIp")