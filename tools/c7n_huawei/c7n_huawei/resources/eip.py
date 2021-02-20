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
from huaweicloudsdkeip.v2 import *

from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiEipFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'eip'

@resources.register('eip')
class Eip(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'eip'
        enum_spec = (None, 'publicips', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListPublicipsRequest()
            response = Session.client(self, service).list_publicips(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response


@Eip.filter_registry.register('unused')
class HuaweiEipFilter(HuaweiEipFilter):
    # 查询指定地域已创建的EIP
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: huawei-eip-unused
               resource: huawei.eip
               filters:
                 - type: unused

    """
    # ACTIVE：已绑定
    # DOWN：未绑定
    schema = type_schema('DOWN')

    def get_request(self, i):
        if i['status'] != "DOWN":
            return False
        return i

@Eip.filter_registry.register('Bandwidth')
class BandwidthEipFilter(HuaweiEipFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下的弹性IP实例是否达到最低带宽要求
            - name: huawei-eip-bandwidth
              resource: huawei.eip
              filters:
                - type: Bandwidth
                  value: 10
    """
    schema = type_schema(
        'Bandwidth',
        **{'value': {'type': 'number'}})

    def get_request(self, i):
        if self.data['value'] < i['bandwidth_size']:
            return False
        return i
