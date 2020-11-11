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

from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from aliyunsdkslb.request.v20140515.DescribeHealthStatusRequest import DescribeHealthStatusRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancerAttributeRequest import DescribeLoadBalancerAttributeRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest

from c7n.utils import type_schema
from c7n_aliyun.client import Session
from c7n_aliyun.filters.filter import AliyunSlbFilter, MetricsFilter, AliyunSlbListenerFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo


@resources.register('slb')
class Slb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'slb'
        enum_spec = (None, 'LoadBalancers.LoadBalancer', None)
        id = 'LoadBalancerId'

    def get_request(self):
        request = DescribeLoadBalancersRequest()
        return request

@Slb.filter_registry.register('unused')
class AliyunSlbFilter(AliyunSlbFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
            - name: aliyun-slb-mark-unused-for-deletion
              resource: aliyun.slb
              filters:
                - type: unused
    """
    # inactive：实例已停止，此状态的实例监听不会再转发流量。
    # active：实例运行中，实例创建后，默认状态为active。
    # locked：实例已锁定，实例已经欠费或被阿里云锁定。
    schema = type_schema('inactive')

    def get_request(self, i):
        LoadBalancerId = i['LoadBalancerId']
        # slb 查询slb下是否有ECS资源
        self.LoadBalancerId = LoadBalancerId
        request = DescribeHealthStatusRequest()
        request.set_LoadBalancerId(LoadBalancerId=self.LoadBalancerId)
        request.set_accept_format('json')
        response_str = Session.client(self, service='ecs').do_action(request)
        response_detail = json.loads(response_str)
        if len(response_detail['BackendServers']['BackendServer']) > 0:
            return None
        return i

@Slb.filter_registry.register('no-listener')
class AliyunSlbFilter(AliyunSlbListenerFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
            - name: aliyun-slb-no-listener
              resource: aliyun.slb
              filters:
                - type: no-listener
    """
    schema = type_schema('no-listener')

    def get_request(self, i):
        request = DescribeLoadBalancerAttributeRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(i['LoadBalancerId'])
        return request

@Slb.filter_registry.register('metrics')
class SlbMetricsFilter(MetricsFilter):

    """
      1              policies:
      2                - name: aliyun-slb
      3                  resource: aliyun.slb
      4                  filters:
      6                    - type: metrics
      7                      name: InstanceTrafficTX
      8                      startTime: '2020-10-08T08:00Z'
      9                      endTime: '2020-11-09T15:30Z'
     10                      statistics: Average
     11                      value: 30000
     12                      op: less-than
    """
    def get_request(self, r):
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_StartTime(self.start)
        request.set_Period(self.period)
        request.set_Namespace(self.namespace)
        request.set_MetricName(self.metric)
        return request

