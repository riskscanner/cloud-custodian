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

service = 'block_store.disk'

@resources.register('disk')
class Disk(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'block_store.disk'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        volumes = Session.client(self, service).volumes(details=False)
        json = dict()  # 创建 {}
        if volumes is not None:
            for name in dir(volumes):
                if not name.startswith('_'):
                    value = getattr(volumes, name)
                    if not callable(value):
                        json[name] = value
        return json


@Disk.action_registry.register('delete')
class DiskDelete(MethodAction):
    """
         policies:
           - name: huawei-disk-delete
             resource: huawei.disk
             actions:
               - delete
     """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}
    attr_filter = ('status', ('available','error',))

    def get_requst(self, disk):
        Session.client(self, service).delete_volume(disk['id'])
        obj = Session.client(self, service).get_volume(disk['id'])
        json = dict()  # 创建 {}
        if obj is not None:
            for name in dir(obj):
                if not name.startswith('_'):
                    value = getattr(obj, name)
                    if not callable(value):
                        json[name] = value
        return json