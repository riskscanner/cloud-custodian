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
from aliyunsdkecs.request.v20140526.DescribeDisksRequest import DescribeDisksRequest
from aliyunsdkecs.request.v20140526.DeleteDiskRequest import DeleteDiskRequest
from c7n.utils import type_schema
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest
from aliyunsdkslb.request.v20140515.DeleteLoadBalancerRequest import DeleteLoadBalancerRequest


@resources.register('slb')
class Slb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'slb'
        enum_spec = (None, 'LoadBalancers.LoadBalancer', None)
        id = 'LoadBalancerId'

    def get_requst(self):
        return DescribeLoadBalancersRequest()


@Slb.action_registry.register('delete')
class SlbDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}


    def get_requst(self, slb):
        request = DeleteLoadBalancerRequest()
        request.set_LoadBalancerId(slb['LoadBalancerId'])
        request.set_accept_format('json')
        return request