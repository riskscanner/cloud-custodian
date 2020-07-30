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

service = 'rdsv3.rds'

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rdsv3.rds'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        query = {
            'offset': 0,
            'limit': 10000
        }
        rds = Session.client(self, service).instances(**query)
        arr = list()  # 创建 []
        if rds is not None:
            for rd in rds:
                json = dict()  # 创建 {}
                for name in dir(rd):
                    if not name.startswith('_'):
                        value = getattr(rd, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr


@Rds.action_registry.register('delete')
class RdsDelete(MethodAction):
    """
        policies:
          - name: huawei-rds-delete
            resource: huawei.rds
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, rds):
        Session.client(self, service).delete_security_group(rds['id'])
        obj = Session.client(self, service).find_security_group(rds['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json