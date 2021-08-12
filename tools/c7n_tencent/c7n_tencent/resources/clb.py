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
from tencentcloud.clb.v20180317 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n_tencent.actions import MethodAction
from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentClbFilter, TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'clb_client.clb'

@resources.register('clb')
class Clb(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'clb_client.clb'
        enum_spec = (None, 'LoadBalancerSet', None)
        id = 'LoadBalancerId'

    def get_request(self):
        offset = 0
        limit = 100
        res = []
        try:
            while 0 <= offset:
                # 实例化一个cvm实例信息查询请求对象,每个接口都会对应一个request对象。
                req = models.DescribeLoadBalancersRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeLoadBalancers(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('LoadBalancerSet', eval(respose))
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
            return False
        return res


@Clb.filter_registry.register('unused')
class TencentClbFilter(TencentClbFilter):
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: tencent-running-clb
               resource: tencent.clb
               filters:
                 - type: unused

    """
    # 负载均衡实例的状态，包括0：创建中，1：正常运行。
    # 注意：此字段可能返回null，表示取不到有效值。
    schema = type_schema('unused')

    def get_request(self, i):
        LoadBalancerId = i.get('LoadBalancerId', '')
        # clb 查询clb下是否有监听
        self.LoadBalancerId = LoadBalancerId
        req = models.DescribeTargetsRequest()
        params = '{"LoadBalancerId" :"' + LoadBalancerId + '"}'
        # params = '{"LoadBalancerIds" :["' + LoadBalancerId + '"]}'
        req.from_json_string(params)

        resp = Session.client(self, service).DescribeTargets(req)
        if len(resp.Listeners) > 0:
            return None
        return i

@Clb.filter_registry.register('acls')
class AclsClbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下CLB不允许任意来源公网访问，视为“合规”
            - name: tencent-clb-acls
              resource: tencent.clb
              filters:
                - type: acls
                  value: INTERNAL
    """
    # 负载均衡实例的网络类型：
    # OPEN：公网属性， INTERNAL：内网属性。
    schema = type_schema(
        'acls',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if i.get('LoadBalancerType', '') and i.get('LoadBalancerType', '') == self.data.get('value', ''):
            return False
        return i

@Clb.filter_registry.register('bandwidth')
class BandwidthClbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下的负载均衡实例是否达到最低带宽要求。
            - name: tencent-clb-bandwidth
              resource: tencent.clb
              filters:
                - type: bandwidth
                  value: 10
    """
    schema = type_schema(
        'bandwidth',
        **{'value': {'type': 'number'}})

    def get_request(self, i):
        InternetMaxBandwidthOut = i.get('NetworkAttributes', {}).get('InternetMaxBandwidthOut', 0)
        if InternetMaxBandwidthOut and self.data.get('value', '') < InternetMaxBandwidthOut:
            return False
        return i


@Clb.filter_registry.register('network-type')
class NetworkTypeClbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下负载均衡实例已关联到VPC；若您配置阈值，则关联的VpcId需存在您列出的阈值中，视为“合规”。
            - name: tencent-clb-network-type
              resource: tencent.clb
              filters:
                - type: network-type
                  value: vpc
    """
    schema = type_schema(
        'network-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if self.data.get('value', '') == "vpc":
            if i.get('VpcId', ''):
                return False
            return i
        else:
            if i.get('VpcId', ''):
                return i
            return False


@Clb.action_registry.register('delete')
class ClbDelete(MethodAction):
    """
         policies:
           - name: tencent-clb-delete
             resource: tencent.clb
             actions:
               - delete
     """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_request(self, clb):
        req = models.DeleteLoadBalancerRequest()
        params = '{"LoadBalancerId" :"' + clb["LoadBalancerId"] + '"}'
        req.from_json_string(params)
        Session.client(self, service).DeleteLoadBalancer