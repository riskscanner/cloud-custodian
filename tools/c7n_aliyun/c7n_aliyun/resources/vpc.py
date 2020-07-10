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

import re

from datetime import datetime

from c7n.utils import type_schema

from c7n_aliyun.actions import MethodAction
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from c7n_aliyun.filters.filter  import SGPermission
from c7n_aliyun.filters.filter  import SGPermissionSchema
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkecs.request.v20140526.DeleteVpcRequest import DeleteVpcRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupsRequest import DescribeSecurityGroupsRequest
from aliyunsdkecs.request.v20140526.DeleteSecurityGroupRequest import DeleteSecurityGroupRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupAttributeRequest import DescribeSecurityGroupAttributeRequest


@resources.register('vpc')
class Vpc(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpc'
        enum_spec = (None, 'Vpcs.Vpc', None)
        id = 'VpcId'

    def get_requst(self):
        request = DescribeVpcsRequest()
        return request



@Vpc.action_registry.register('delete')
class Delete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, vpc):
        request = DeleteVpcRequest()
        request.set_InstanceId(vpc['VpcId'])
        request.set_accept_format('json')
        return request



@resources.register('security-group')
class SecurityGroup(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'security-group'
        enum_spec = (None, 'SecurityGroups.SecurityGroup', None)
        id = 'SecurityGroupId'

    def get_requst(self):
        request = DescribeSecurityGroupsRequest()
        return request

@SecurityGroup.filter_registry.register('ingress')
class IPPermission(SGPermission):

    ip_permissions_key = "Permissions.Permission"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['ingress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def process_self_cidrs(self, perm):
        self.process_cidrs(perm, "SourceCidrIp", "Ipv6SourceCidrIp")


    def securityGroupAttributeRequst(self, sg):
        requst = DescribeSecurityGroupAttributeRequest();
        requst.set_SecurityGroupId(sg["SecurityGroupId"])
        requst.set_Direction("egress")
        requst.set_accept_format('json')
        return requst

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
        requst = DescribeSecurityGroupAttributeRequest();
        requst.set_SecurityGroupId(sg["SecurityGroupId"])
        requst.set_Direction("egress")
        requst.set_accept_format('json')
        return requst

    def process_self_cidrs(self, perm):
        self.process_cidrs(perm, "DestCidrIp", "Ipv6DestCidrIp")





@SecurityGroup.action_registry.register('delete')
class Delete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, sg):
        request = DeleteSecurityGroupRequest()
        request.set_InstanceId(sg['SecurityGroupId'])
        request.set_accept_format('json')
        return request

