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
import os

from openstack import connection

from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo


@resources.register('ecs')
class Ecs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'compute.ecs'
        enum_spec = (None, None, None)
        id = 'InstanceId'
        dimension = 'InstanceId'

    def get_requst(self):
        conn = connection.Connection(
            cloud="myhuaweicloud.com",
            ak=os.getenv('HUAWEI_AK'),
            sk=os.getenv('HUAWEI_SK'),
            region=os.getenv('HUAWEI_DEFAULT_REGION'),
            project_id=os.getenv('HUAWEI_PROJECT')
        )
        servers = conn.compute.servers(limit=10000)
        arr = list() # 创建 []
        for server in servers:
            json = dict() # 创建 {}
            for name in dir(server):
                if not name.startswith('_'):
                    value = getattr(server, name)
                    if not callable(value):
                        json[name] = value
            arr.append(json)
        return arr
