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



@resources.register('disk')
class Disk(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'disk'
        enum_spec = (None, 'Disks.Disk', None)
        id = 'DiskId'

    def get_requst(self):
        request = DescribeDisksRequest()
        return request


@Disk.action_registry.register('delete')
class DiskDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}
    attr_filter = ('Status', ('Available', ))

    def get_requst(self, disk):
        request = DeleteDiskRequest()
        request.set_DiskId(disk['DiskId'])
        request.set_accept_format('json')
        return request