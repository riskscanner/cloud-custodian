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
from c7n_huawei.filters.filter import HuaweiElbFilter

service = 'network.elb'

@resources.register('elb')
class Elb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'network.elb'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        lbs = Session.client(self, service).loadbalancers()
        arr = list()  # 创建 []
        if lbs is not None:
            for slb in lbs:
                json = dict()  # 创建 {}
                for name in dir(slb):
                    if not name.startswith('_'):
                        value = getattr(slb, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr


@Elb.filter_registry.register('unused')
class HuaweiElbFilter(HuaweiElbFilter):
    # 查询指定地域已创建的EIP
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: huawei-elb
               resource: huawei.elb
               filters:
                 - type: unused

    """
    # Associating：绑定中。
    # Unassociating：解绑中。
    # InUse：已分配。
    # Available：可用。
    schema = type_schema('Available')

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
        obj = Session.client(self, service).delete_loadbalancer(elb['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json