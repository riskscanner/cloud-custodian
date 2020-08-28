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
import json
import logging

from aliyunsdkrds.request.v20140815.DescribeRegionsRequest import DescribeRegionsRequest
from aliyunsdkrds.request.v20140815.DeleteDBInstanceRequest import DeleteDBInstanceRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from aliyunsdkcore import client
from c7n.utils import type_schema

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
service = 'rds'
accessKeyId = os.getenv('ALIYUN_ACCESSKEYID')
accessSecret = os.getenv('ALIYUN_ACCESSSECRET')
regionId = os.getenv('ALIYUN_DEFAULT_REGION')

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rds'
        enum_spec = (None, 'Items.DBInstance', None)
        id = 'DBInstanceId'

    def get_requst(self):
        clt = client.AcsClient(accessKeyId, accessSecret, "cn-beijing")
        request = DescribeRegionsRequest()
        request.set_accept_format('json')
        response_str = clt.do_action(request)
        response = json.loads(response_str)
        if response is not None:
            region_list = response.get('Regions').get('RDSRegion')
        flag = False
        for res in region_list:
            if regionId == res['RegionId']:
                flag = True
                break
        if flag:
            # 乌兰察布暂时不支持rds
            return DescribeDBInstancesRequest()
        else:
            logging.error("RDS service in this region is not supported!")
            return False

@Rds.action_registry.register('delete')
class RdsDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}


    def get_requst(self, rds):
        request = DeleteDBInstanceRequest()
        request.set_DBInstanceId(rds['DBInstanceId'])
        request.set_accept_format('json')
        return request