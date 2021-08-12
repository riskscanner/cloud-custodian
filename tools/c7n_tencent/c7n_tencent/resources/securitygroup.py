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
import json
import logging

import jmespath
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import models

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import SGPermission
from c7n_tencent.filters.filter import SGPermissionSchema, TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'vpc_client.security-group'

@resources.register('security-group')
class SecurityGroup(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpc_client.security-group'
        enum_spec = (None, 'SecurityGroupSet', None)
        id = 'SecurityGroupId'

    def get_request(self):
        # 为什么设置成字符串，不晓得sd可怎么设计的，全靠猜。
        offset = '0'
        limit = '100'
        res = []
        try:
            while 0 <= int(offset):
                req = models.DescribeSecurityGroupsRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeSecurityGroups(req)
                for sg in resp.SecurityGroupSet:
                    req2 = models.DescribeSecurityGroupPoliciesRequest()
                    params = '{"SecurityGroupId":"' + sg.SecurityGroupId + '"}'
                    req2.from_json_string(params)
                    resp2 = Session.client(self, service).DescribeSecurityGroupPolicies(req2)
                    sg.IpPermissions = resp2.SecurityGroupPolicySet
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('SecurityGroupSet', eval(respose))
                res = res + result
                if len(result) == limit:
                    offset += 1
                else:
                    return res
                # 输出json格式的字符串回包
                # print(resp.to_json_string(indent=2))

                # 也可以取出单个值。
                # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
                # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            logging.error(err)
        return res


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

    def get_request(self, security_group):
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
                        IpProtocol: TCP
                        Ports: [20,21,22,25,80,443,465,1433,1434,3306,3389,4333,5432,5500]
                        Cidr: "0.0.0.0/0"
                      - type: ingress
                        IpProtocol: TCP
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
        return self.process_cidrs(perm, 'CidrBlock', 'Ipv6CidrBlock')

    def securityGroupAttributeRequst(self, sg):
        self.direction = 'Ingress'
        req = models.DescribeSecurityGroupsRequest()
        params = '{"SecurityGroupId" :"' + sg["SecurityGroupId"] + '"}'
        req.from_json_string(params)
        resp = Session.client(self, service).DescribeSecurityGroups(req)
        for res in resp.SecurityGroupSet:
            if sg["SecurityGroupId"] != res.SecurityGroupId:
                continue
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
        self.direction = 'Egress'
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
        return self.process_cidrs(perm, "CidrBlock", "Ipv6CidrBlock")


@SecurityGroup.filter_registry.register('source-cidr-ip')
class SourceCidrIp(TencentFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下CVM安全组配置不为“0.0.0.0/0”，视为“合规”。
            - name: tencent-sg-source-cidr-ip
              resource: tencent.security-group
              filters:
                - type: source-cidr-ip
                  value: "0.0.0.0/0"
    """

    ip_permissions_key = "IpPermissions.Ingress"
    schema = type_schema(
        'source-cidr-ip',
        **{'value': {'type': 'string'}})

    def get_request(self, sg):
        for cidr in jmespath.search(self.ip_permissions_key, sg):
            if cidr['CidrBlock'] == self.data.get('value', ''):
                return sg
        return False