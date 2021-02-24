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
from huaweicloudsdkvpc.v2 import *

from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiVpcFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'vpc'
@resources.register('vpc')
class Vpc(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpc'
        enum_spec = (None, 'vpcs', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListVpcsRequest()
            response = Session.client(self, service).list_vpcs(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@Vpc.filter_registry.register('unused')
class HuaweiVpcFilter(HuaweiVpcFilter):
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: huawei-vpc
               resource: huawei.vpc
               filters:
                 - type: unused

    """

    def get_request(self, i):
        #vpc 查询vpc配额，used：已创建的资源个数
        request = ShowQuotaRequest()
        request.type = "vpc"
        response = Session.client(self, service).show_quota(request)
        for object in response.quotas.resources:
            # 资源：弹性云服务器、裸金属服务、弹性负载均衡器
            if object.used > 0:
                return None
        return i