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
service = 'redis'

@resources.register('redis')
class Redis(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'redis'
        enum_spec = (None, 'instances', None)
        id = 'instance_id'

    def get_request(self):
        try:
            request = ListInstancesRequest()
            response = Session.client(self, service).list_instances(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@Redis.filter_registry.register('internet-access')
class InternetAccessRedisFilter(HuaweiRedisFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下Redis实例不允许任意来源公网访问，视为“合规”
            - name: huawei-redis-internet-access
              resource: huawei.redis
              filters:
                - type: internet-access
                  value: true
    """

    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        public_ips = i['publicip_id']
        if self.data.get('value', ''):
            if public_ips is None or (len(public_ips) == 0 and i['enable_ssl'] == False):
                return i
            return False
        else:
            if public_ips is None:
                return False
            if len(public_ips) > 0 and i['enable_ssl'] == True:
                return i
            return False

@Redis.filter_registry.register('no-password-access')
class NoPasswordAccessRedisFilter(HuaweiRedisFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下Redis实例是否允许免密码访问，不允许视为“合规”，否则视为“不合规”
            - name: huawei-redis-no-password-access
              resource: huawei.redis
              filters:
                - type: no-password-access
                  value: true
    """

    schema = type_schema(
        'no-password-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        if i['no_password_access'] == self.data.get('value', ''):
            return i
        return False
