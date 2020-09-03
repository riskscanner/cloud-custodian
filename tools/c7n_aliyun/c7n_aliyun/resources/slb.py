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

from aliyunsdkslb.request.v20140515.DeleteLoadBalancerRequest import DeleteLoadBalancerRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.filters.filter import AliyunSlbFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.utils import type_schema


@resources.register('slb')
class Slb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'slb'
        enum_spec = (None, 'LoadBalancers.LoadBalancer', None)
        id = 'LoadBalancerId'

    def get_request(self):
        request = DescribeLoadBalancersRequest()
        return request

@Slb.filter_registry.register('inactive')
class AliyunSlbFilter(AliyunSlbFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
            - name: aliyun-elb-mark-unused-for-deletion
              resource: aliyun.slb
              filters:
                - inactive
              actions:
                - delete
    """
    # inactive：实例已停止，此状态的实例监听不会再转发流量。
    # active：实例运行中，实例创建后，默认状态为active。
    # locked：实例已锁定，实例已经欠费或被阿里云锁定。
    schema = type_schema('inactive')


@Slb.action_registry.register('delete')
class SlbDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}


    def get_request(self, slb):
        request = DeleteLoadBalancerRequest()
        request.set_LoadBalancerId(slb['LoadBalancerId'])
        request.set_accept_format('json')
        return request