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

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import models

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import SGPermission
from c7n_tencent.filters.filter import SGPermissionSchema
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'vpc_client.security-group'

@resources.register('security-group')
class SecurityGroup(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpc_client.security-group'
        enum_spec = (None, 'SecurityGroupSet', None)
        id = 'SecurityGroupId'

    def get_requst(self):
        try:
            req = models.DescribeSecurityGroupsRequest()
            resp = Session.client(self, service).DescribeSecurityGroups(req)
            for res in resp.SecurityGroupSet:
                req2 = models.DescribeSecurityGroupPoliciesRequest()
                params = '{"SecurityGroupId":"' + res.SecurityGroupId + '"}'
                req2.from_json_string(params)
                resp2 = Session.client(self, service).DescribeSecurityGroupPolicies(req2)
                res.IpPermissions = resp2.SecurityGroupPolicySet
            # 输出json格式的字符串回包
            # print(resp.to_json_string(indent=2))

            # 也可以取出单个值。
            # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
            # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            logging.error(err)
            return False
        # tencent 返回的json里居然不是None，而是java的null，活久见
        return resp.to_json_string().replace('null', 'None')


@SecurityGroup.action_registry.register('delete')
class Delete(MethodAction):

    """
        policies:
          - name: tencent-security-group-delete
            resource: tencent.security-group
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, security_group):
        req = models.DeleteSecurityGroupRequest()
        params = '{"SecurityGroupId" :"' + security_group["SecurityGroupId"] + '"}'
        req.from_json_string(params)
        Session.client(self, service).DeleteSecurityGroup(req)

@SecurityGroup.filter_registry.register('ingress')
class IPPermission(SGPermission):

    """
        policies:
            #扫描开放以下高危端口的安全组：
            #(20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500)
            - name: tencent-security-group
              resource: tencent.security-group
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
    ip_permissions_key = "SecurityGroupSet"
    ip_permissions_type = "ingress"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['ingress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def process_self_cidrs(self, perm):
        self.process_cidrs(perm, 'CidrBlock', 'Ipv6CidrBlock')

    def securityGroupAttributeRequst(self, sg):
        req = models.DescribeSecurityGroupsRequest()
        params = '{"SecurityGroupId" :"' + sg["SecurityGroupId"] + '"}'
        req.from_json_string(params)
        resp = Session.client(self, service).DescribeSecurityGroups(req)
        for res in resp.SecurityGroupSet:
            req2 = models.DescribeSecurityGroupPoliciesRequest()
            params = '{"SecurityGroupId":"' + res.SecurityGroupId + '"}'
            req2.from_json_string(params)
            resp2 = Session.client(self, service).DescribeSecurityGroupPolicies(req2)
            res.IpPermissions = resp2.SecurityGroupPolicySet
        return resp.to_json_string().replace('null', 'None')

@SecurityGroup.filter_registry.register('egress')
class IPPermission(SGPermission):
    ip_permissions_key = "Permissions.Permission"
    ip_permissions_type = "egress"
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'type': {'enum': ['egress']}},
        'required': ['type']}
    schema['properties'].update(SGPermissionSchema)

    def securityGroupAttributeRequst(self, sg):
        req = models.DescribeSecurityGroupsRequest()
        params = '{"SecurityGroupId" :"' + sg["SecurityGroupId"] + '"}'
        req.from_json_string(params)
        resp = Session.client(self, service).DescribeSecurityGroups(req)
        for res in resp.SecurityGroupSet:
            req2 = models.DescribeSecurityGroupPoliciesRequest()
            params = '{"SecurityGroupId":"' + res.SecurityGroupId + '"}'
            req2.from_json_string(params)
            resp2 = Session.client(self, service).DescribeSecurityGroupPolicies(req2)
            res.IpPermissions = resp2.SecurityGroupPolicySet
        return resp.to_json_string().replace('null', 'None')

def process_self_cidrs(self, perm):
        self.process_cidrs(perm, "CidrBlock", "Ipv6CidrBlock")