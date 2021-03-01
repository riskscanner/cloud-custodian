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
import logging

import urllib3
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkdcs.v2 import *
from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiRedisFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'dds'

@resources.register('dds')
class Dds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'dds'
        enum_spec = (None, 'instances', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListInstancesRequest()
            response = Session.client(self, service).list_instances(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@Dds.filter_registry.register('InternetAccess')
class InternetAccessRedisFilter(HuaweiRedisFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下Redis实例不允许任意来源公网访问，视为“合规”
            - name: huawei-redis-internet-access
              resource: huawei.redis
              filters:
                - type: InternetAccess
                  value: true
    """

    schema = type_schema(
        'InternetAccess',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        groups = i['groups']
        if self.data['value']:
            if len(groups) > 0:
                for group in groups:
                    if len(group['nodes']) > 0:
                        if group['nodes']['public_ip']:
                            return i
            return None
        else:
            if len(groups) == 0:
                return i
            else:
                for group in groups:
                    if len(group['nodes']) > 0:
                        if group['nodes']['public_ip']:
                            return i
                return None

