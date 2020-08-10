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

from aliyunsdkecs.request.v20140526.DescribeEipAddressesRequest import DescribeEipAddressesRequest
from aliyunsdkecs.request.v20140526.ReleaseEipAddressRequest import ReleaseEipAddressRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.filters.filter import AliyunEipFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.utils import type_schema


@resources.register('eip')
class Eip(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'eip'
        enum_spec = (None, 'EipAddresses.EipAddress', None)
        id = 'AllocationId'

    def get_requst(self):
        request = DescribeEipAddressesRequest()
        return request

@Eip.filter_registry.register('unused')
class AliyunEipFilter(AliyunEipFilter):
    # 查询指定地域已创建的EIP
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
             - name: aliyun-eip
               resource: aliyun.eip
               filters:
                 - type: unused
    """
    # Associating：绑定中。
    # Unassociating：解绑中。
    # InUse：已分配。
    # Available：可用。
    schema = type_schema('Available')

@Eip.action_registry.register('release')
class EipRelease(MethodAction):
    """Filters:

       :Example:

       .. code-block:: yaml

           policies:
             #释放未连接的弹性IP
             - name: aliyun-eip
               resource: aliyun.eip
               filters:
                 - type: unused
               actions:
                 - release
    """
    # 释放指定的EIP
    schema = type_schema('release')
    method_spec = {'op': 'release'}

    def get_requst(self, eip):
        request = ReleaseEipAddressRequest()
        request.set_AllocationId(eip['AllocationId'])
        request.set_accept_format('json')
        return request        
