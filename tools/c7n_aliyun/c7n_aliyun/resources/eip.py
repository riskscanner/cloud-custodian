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

from c7n.utils import type_schema

from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from aliyunsdkecs.request.v20140526.DescribeEipAddressesRequest import DescribeEipAddressesRequest


@resources.register('eip')
class Vpc(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'eip'
        enum_spec = (None, 'Eip.Eip', None)
        id = 'AllocationId'

    def get_requst(self):
        request = DescribeEipAddressesRequest()
        return request

