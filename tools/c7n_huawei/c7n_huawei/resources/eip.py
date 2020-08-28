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
from c7n_huawei.filters.filter import HuaweiEipFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'network.eip'

@resources.register('eip')
class Eip(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'network.eip'
        enum_spec = (None, None, None)
        id = 'id'

    def get_requst(self):
        query = {
            "limit": 10000
        }
        ips = Session.client(self, service).ips(**query)
        arr = list()  # 创建 []
        if ips is not None:
            for ip in ips:
                json = dict()  # 创建 {}
                for name in dir(ip):
                    if not name.startswith('_'):
                        value = getattr(ip, name)
                        if not callable(value):
                            json[name] = value
                arr.append(json)
        return arr


@Eip.filter_registry.register('unused')
class HuaweiEipFilter(HuaweiEipFilter):
    # 查询指定地域已创建的EIP
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: huawei-eip
               resource: huawei.eip
               filters:
                 - type: unused

    """
    # ACTIVE：已绑定
    # DOWN：未绑定
    schema = type_schema('DOWN')

@Eip.action_registry.register('delete')
class EipRelease(MethodAction):
    # 释放指定的EIP
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_requst(self, eip):
        Session.client(self, service).delete_ip(eip['id'])
