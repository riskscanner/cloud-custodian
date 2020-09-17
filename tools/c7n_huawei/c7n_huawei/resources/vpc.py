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
import os
from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiVpcFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'vpcv1.vpc'
project_id = os.getenv('HUAWEI_PROJECT')

@resources.register('vpc')
class Vpc(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpcv1.vpc'
        enum_spec = (None, None, None)
        id = 'id'

    def get_request(self):
        query = {
            "limit": 10000
        }
        try:
            vpcs = Session.client(self, service).vpcs(**query)
            arr = list() # 创建 []
            if vpcs is not None:
                for vpc in vpcs:
                    json = dict() # 创建 {}
                    json = Session._loads_(json, vpc)
                    arr.append(json)
        except Exception as err:
            pass
        return arr


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
    # CREATING：创建中
    # OK：创建成功
    schema = type_schema('OK')

    def get_request(self, i):
        VpcId = i['name']
        #vpc 查询vpc配额，used：已创建的资源个数
        # query = {
        #     "limit": 100,
        #     "project_id": project_id,
        #     "vpc_id": VpcId
        # }
        # objs = Session.client(self, service).quotas(**query)
        # arr = list()  # 创建 []
        # if objs is not None:
        #     for obj in objs:
        #         json = dict()  # 创建 {}
        #         json = Session._loads_(json, obj)
        #         arr.append(json)
        # for object in arr:
        #     # 资源：弹性云服务器、裸金属服务、弹性负载均衡器
        #     if object['type'] in ['loadbalancer', 'listener', 'physicalConnect']:
        #         if object['used'] > 0:
        #             return None
        return i

@Vpc.action_registry.register('delete')
class Delete(MethodAction):

    """
        policies:
          - name: huawei-vpc-delete
            resource: huawei.vpc
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_request(self, vpc):
        Session.client(self, service).delete_vpc(vpc['id'])