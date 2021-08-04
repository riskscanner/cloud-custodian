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

import jmespath
import urllib3
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkelb.v2 import *

from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiElbFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'elb'

@resources.register('elb')
class Elb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'elb'
        enum_spec = (None, 'loadbalancers', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListLoadbalancersRequest()
            response = Session.client(self, service).list_loadbalancers(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@Elb.filter_registry.register('listener')
class ListenerElbFilter(HuaweiElbFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 负载均衡开启HTTPS监听，视为“合规”。
            - name: huawei-elb-listener
              resource: huawei.elb
              filters:
                - type: listener
                  value: https
    """
    schema = type_schema(
        'listener',
        **{'value': {'type': 'string'}})
    listener_protocol_key = "listeners"
    filter = None

    def get_request(self, i):
        for data in jmespath.search(self.listener_protocol_key, i):
            request = ShowListenerRequest()
            request.listener_id = data
            response = Session.client(self, service).show_listener(request)
            if jmespath.search('protocol', response) == self.data.get('value', ''):
                return False
        return i


@Elb.filter_registry.register('unused')
class UnusedElbFilter(HuaweiElbFilter):
    """Filters:Example:
       .. code-block:: yaml

           policies:
             # 账号下负载均衡实例是否已关联到后端云服务器组；若关联，视为“合规”，否则视为不合规。
             - name: huawei-elb-unused
               resource: huawei.elb
               filters:
                 - type: unused

    """
    # 负载均衡器关联的后端云服务器组ID的列表。。
    schema = type_schema('unused')

    def get_request(self, i):
        listeners = i.get('pools', [])
        # elb 查询elb下是否有监听
        if len(listeners) > 0:
            return False
        return i

@Elb.filter_registry.register('address-type')
class AddressTypeElbFilter(HuaweiElbFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 负载均衡实例未直接绑定公网IP，视为“合规”。该规则仅适用于 IPv4 协议。
            - name: huawei-elb-address-type
              resource: huawei.elb
              filters:
                - type: address-type
                  value: internet
    """
    # internet 公网/intranet 内网
    schema = type_schema(
        'address-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if self.data.get('value', '') == 'internet':
            if i.get('vip_address', '')  is not None:
                return False
        else:
            if i.get('vip_address', '') is None:
                return False
        return i