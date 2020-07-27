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

from aliyunsdkrds.request.v20140815.DeleteDBInstanceRequest import DeleteDBInstanceRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.utils import type_schema


@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rds'
        enum_spec = (None, 'Items.DBInstance', None)
        id = 'DBInstanceId'

    def get_requst(self):
        return DescribeDBInstancesRequest()


@Rds.action_registry.register('delete')
class SlbDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}


    def get_requst(self, rds):
        request = DeleteDBInstanceRequest()
        request.set_DBInstanceId(rds['DBInstanceId'])
        request.set_accept_format('json')
        return request