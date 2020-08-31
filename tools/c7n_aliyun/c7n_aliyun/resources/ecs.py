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

import operator

from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.filters.filter import AliyunAgeFilter
from c7n_aliyun.filters.filter import MetricsFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.utils import type_schema


@resources.register('ecs')
class Ecs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'ecs'
        enum_spec = (None, 'Instances.Instance', None)
        id = 'InstanceId'
        dimension = 'InstanceId'

    def get_request(self):
        request = DescribeInstancesRequest()
        return request


@Ecs.filter_registry.register('instance-age')
class EcsAgeFilter(AliyunAgeFilter):
    """Filters instances based on their age (in days)

    :Example:

    .. code-block:: yaml

        policies:
          - name: ecs-30-days-plus
            resource: aliyun.ecs
            filters:
              - type: instance-age
                op: ge
                minutes: 1
    """

    date_attribute = "LaunchTime"
    ebs_key_func = operator.itemgetter('AttachTime')

    schema = type_schema(
        'instance-age',
        op={'$ref': '#/definitions/filters_common/comparison_operators'},
        days={'type': 'number'},
        hours={'type': 'number'},
        minutes={'type': 'number'})

    def get_resource_date(self, i):
        return i['CreationTime']

@Ecs.filter_registry.register('metrics')
class EcsMetricsFilter(MetricsFilter):

    def get_request(self):
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        return request


@Ecs.action_registry.register('start')
class Start(MethodAction):

    schema = type_schema('start')
    method_spec = {'op': 'start'}
    attr_filter = ('Status', ('Stopped',))

    def get_request(self, instance):
        request = StartInstanceRequest()
        request.set_InstanceId(instance['InstanceId'])
        request.set_accept_format('json')
        return request

@Ecs.action_registry.register('stop')
class Stop(MethodAction):

    schema = type_schema('stop')
    method_spec = {'op': 'stop'}
    attr_filter = ('Status', ('Running',))

    def get_request(self, instance):
        request = StopInstanceRequest()
        request.set_InstanceId(instance['InstanceId'])
        request.set_ForceStop(True)
        request.set_accept_format('json')
        return  request


@Ecs.action_registry.register('delete')
class Delete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_request(self, instance):
        request = DeleteInstanceRequest()
        request.set_InstanceId(instance['InstanceId'])
        request.set_accept_format('json')
        return request
