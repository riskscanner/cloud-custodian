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
import os

import jmespath
from aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkdds.request.v20151201.DescribeSecurityIpsRequest import DescribeSecurityIpsRequest
from aliyunsdkdds.request.v20151201.DescribeSecurityGroupConfigurationRequest import DescribeSecurityGroupConfigurationRequest



from c7n.utils import type_schema
from c7n_aliyun.filters.filter import AliyunRdsFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from c7n_aliyun.client import Session

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')

service = 'mongodb'
regionId = os.getenv('ALIYUN_DEFAULT_REGION')

@resources.register('mongodb')
class MongoDB(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'mongodb'
        enum_spec = (None, 'Instances.KVStoreInstance', None)
        id = 'InstanceId'

    def get_request(self):
        return DescribeInstancesRequest()

@MongoDB.filter_registry.register('network-type')
class NetworkTypeMongoDBFilter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下的MongoDB实例是否运行在VPC网络环境下
            - name: aliyun-mongodb-network-type
              resource: aliyun.mongodb
              filters:
                - type: network-type
                  value: VPC
    """
    # 实例的网络类型，取值：
    #
    # Classic：经典网络
    # VPC：VPC网络
    schema = type_schema(
        'network-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if self.data['value'] == i['NetworkType']:
            return False
        return i

@MongoDB.filter_registry.register('internet-access')
class InternetAccessMongoDBFilter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下MongoDB实例不允许任意来源公网访问，视为“合规”
            - name: aliyun-mongodb-internet-access
              resource: aliyun.mongodb
              filters:
                - type: internet-access
                  value: true
    """
    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        request1 = DescribeSecurityIpsRequest()
        request1.set_accept_format('json')
        response1 = Session.client(self, service).do_action_with_exception(request1)
        string1 = str(response1, encoding="utf-8").replace("false", "False")
        SecurityIpGroups = jmespath.search('SecurityIpGroups.SecurityIpGroup', eval(string1))

        request2 = DescribeSecurityGroupConfigurationRequest()
        request2.set_accept_format('json')
        response2 = Session.client(self, service).do_action_with_exception(request2)
        string2 = str(response2, encoding="utf-8").replace("false", "False")

        RdsEcsSecurityGroupRel = jmespath.search('Items.RdsEcsSecurityGroupRel', eval(string2))
        if self.data['value']:
            if len(SecurityIpGroups) == 0 and len(RdsEcsSecurityGroupRel) == 0:
                return False
        else:
            return False
        i['SecurityIpGroups'] = SecurityIpGroups
        i['RdsEcsSecurityGroupRel'] = RdsEcsSecurityGroupRel
        return i