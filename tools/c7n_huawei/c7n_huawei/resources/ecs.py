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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiAgeFilter
from c7n_huawei.filters.filter import MetricsFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'compute.ecs'

@resources.register('ecs')
class Ecs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'compute.ecs'
        enum_spec = (None, None, None)
        id = 'id'
        dimension = 'id'

    def get_request(self):
        servers = Session.client(self, service).servers(limit=10000)
        arr = list()  # 创建 []
        if servers is not None:
            for server in servers:
                json = dict()  # 创建 {}
                for name in dir(server):
                    if not name.startswith('_'):
                        value = getattr(server, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr

@Ecs.filter_registry.register('metrics')
class EcsMetricsFilter(MetricsFilter):

    def get_request(self):
        servers = Session.client(self, service).servers(limit=10000)
        arr = list()  # 创建 []
        if servers is not None:
            for server in servers:
                json = dict()  # 创建 {}
                for name in dir(server):
                    if not name.startswith('_'):
                        value = getattr(server, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr

@Ecs.filter_registry.register('instance-age')
class EcsAgeFilter(HuaweiAgeFilter):
    """Filters instances based on their age (in days)
        policies:
          - name: huawei-ecs-30-days-plus
            resource: huawei.ecs
            filters:
              - type: instance-age
                op: lt
                days: 30
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
        # '2020-07-27T05:55:32.000000'
        return i['launched_at']

@Ecs.action_registry.register('start')
class Start(MethodAction):
    """
        policies:
          - name: huawei-ecs-start
            resource: huawei.ecs
            actions:
              - start
    """

    schema = type_schema('start')
    method_spec = {'op': 'start'}
    attr_filter = ('status', ('SHUTOFF',))

    def get_request(self, instance):
        Session.client(self, service).start_server(instance['id'])

@Ecs.action_registry.register('stop')
class Stop(MethodAction):
    """
        policies:
          - name: huawei-ecs-stop
            resource: huawei.ecs
            actions:
              - stop
    """
    schema = type_schema('stop')
    method_spec = {'op': 'stop'}
    attr_filter = ('status', ('ACTIVE',))

    def get_request(self, instance):
        Session.client().stop_server(instance['id'])

@Ecs.action_registry.register('delete')
class Delete(MethodAction):
    """
        policies:
          - name: huawei-ecs-delete
            resource: huawei.ecs
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}
    attr_filter = ('status', ('SHUTOFF',))

    def get_request(self, instance):
        Session.client(self, service).delete_server(instance['id'])