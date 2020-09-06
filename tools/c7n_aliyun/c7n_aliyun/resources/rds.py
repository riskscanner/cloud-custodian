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
import os

from aliyunsdkrds.request.v20140815.DeleteDBInstanceRequest import DeleteDBInstanceRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.filters.filter import AliyunRdsFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.utils import type_schema

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')

service = 'rds'
regionId = os.getenv('ALIYUN_DEFAULT_REGION')

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rds'
        enum_spec = (None, 'Items.DBInstance', None)
        id = 'DBInstanceId'

    def get_request(self):
        try:
            # clt = Session.client(self, service)
            # request = DescribeRegionsRequest()
            # request.set_accept_format('json')
            # response_str = clt.do_action_with_exception(request)
            # response = json.loads(response_str)
            """
                aliyunsdkcore.client:ERROR ServerException occurred. Host:location-readonly.aliyuncs.com SDK-Version:2.13.11 
                ServerException:HTTP Status: 404 Error:InvalidRegionId The specified region does not exist. 
                RequestID: 4B62B859-1CBD-46E9-9A41-A2F5FD672E2C
                用DescribeRegionsRequest去查,sdk直接会抛出ERROR异常，虽然不影响返回的数据，但是在安全合规模块遇到ERROR会报错。所以暂时写死region
            """
            if regionId == "cn-wulanchabu":
                flag = False
            else:
                flag = True
            # if response is not None:
            #     region_list = response.get('Regions').get('RDSRegion')
            #     for res in region_list:
            #         if regionId == res['RegionId']:
            #             flag = True
            #             break
        except Exception as error:
            logging.warn(error)
            flag = False
        if flag:
            # 乌兰察布暂时不支持rds
            return DescribeDBInstancesRequest()
        else:
            logging.warn("RDS service in %s is not supported!", regionId)
            return flag

@Rds.filter_registry.register('Internet')
class AliyunRdsFilter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            - name: aliyun-rds
              resource: aliyun.rds
              filters:
                - type: Internet
    """
    # 实例是内网或外网，取值：
    #
    # Internet：外网
    # Intranet：内网
    schema = type_schema('Internet')

@Rds.action_registry.register('delete')
class RdsDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}


    def get_request(self, rds):
        request = DeleteDBInstanceRequest()
        request.set_DBInstanceId(rds['DBInstanceId'])
        request.set_accept_format('json')
        return request