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
from huaweicloudsdkiam.v3 import *

from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiIamFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo
from c7n.utils import type_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'iam'

@resources.register('iam')
class Iam(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'iam'
        enum_spec = (None, 'login_protects', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListUserLoginProtectsRequest()
            response = Session.client(self, service).list_user_login_protects(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response


@Iam.filter_registry.register('login')
class HuaweiIamLoginFilter(HuaweiIamFilter):
    """Filters
       :Example:

       .. code-block:: yaml

           policies:
            # 检测IAM用户是否开启登录保护，开启视为“合规”，否则属于“不合规”
            - name: huawei-iam-login
              resource: huawei.iam
              filters:
                - type: login
                  value: true
    """
    schema = type_schema(
        'login',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        if self.data['value'] == i['enabled']:
            return False
        return i