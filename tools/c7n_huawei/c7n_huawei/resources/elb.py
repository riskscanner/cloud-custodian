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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'network.elb'

@resources.register('elb')
class Elb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'network.elb'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        lbs = Session.client(self, service).loadbalancers()
        json = dict()  # 创建 {}
        if lbs is not None:
            for name in dir(lbs):
                if not name.startswith('_'):
                    value = getattr(lbs, name)
                    if not callable(value):
                        json[name] = value
        return json


@Elb.action_registry.register('delete')
class ElbDelete(MethodAction):
    """
         policies:
           - name: huawei-elb-delete
             resource: huawei.elb
             actions:
               - delete
     """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, elb):
        Session.client(self, service).delete_loadbalancer(elb['id'])
        obj = Session.client(self, service).get_loadbalancer(elb['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json