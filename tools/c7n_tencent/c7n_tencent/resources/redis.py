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
from tencentcloud.redis.v20180412 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'redis_client.redis'

@resources.register('redis')
class Redis(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'redis_client.redis'
        enum_spec = (None, 'InstanceSet', None)
        id = 'InstanceId'

    def get_request(self):
        offset = 0
        limit = 20
        res = []
        try:
            while 0 <= offset:
                req = models.DescribeInstancesRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeInstances(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('InstanceSet', eval(respose))
                res = res + result
                if len(result) == limit:
                    offset += limit
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

@Redis.filter_registry.register('network-type')
class NetworkTypeRedisFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下的Redis实例是否运行在VPC网络环境下
            - name: tencent-redis-network-type
              resource: tencent.redis
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

@Redis.filter_registry.register('internet-access')
class InternetAccessRedisFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下Redis实例不允许任意来源公网访问，视为“合规”
            - name: tencent-redis-internet-access
              resource: tencent.redis
              filters:
                - type: internet-access
                  value: true
    """
    # 网络类型，可能的返回值：0-基础网络，1-私有网络

    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        if self.data.get('value', ''):
            if i.get('NetType', '') == 0:
                return i
        else:
            if i.get('NetType', '') != 0:
                return i
        return False