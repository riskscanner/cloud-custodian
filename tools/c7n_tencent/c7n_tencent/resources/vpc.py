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
import json
import logging

import jmespath
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import models

from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentVpcFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo
from c7n_tencent.resources.clb import Clb
from c7n_tencent.resources.cvm import Cvm

service = 'vpc_client.vpc'

@resources.register('vpc')
class Vpc(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'vpc_client.vpc'
        enum_spec = (None, 'VpcSet', None)
        id = 'VpcId'

    def get_request(self):
        offset = 0
        limit = 20
        res = []
        try:
            while 0 <= offset:
                req = models.DescribeVpcsRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeVpcs(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('VpcSet', eval(respose))
                res = res + result
                if len(result) == limit:
                    offset += limit
                else:
                    return res
                # 输出json格式的字符串回包
                # print(resp.to_json_string(indent=2))

                # 也可以取出单个值。
                # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
                # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            logging.error(err)
        return res

@Vpc.filter_registry.register('unused')
class TencentVpcFilter(TencentVpcFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            - name: tencent-avalible-vpc
              resource: tencent.vpc
              filters:
                - type: unused
    """
    schema = type_schema('AVAILABLE')

    def get_request(self, i):
        VpcId = i.get('VpcId', '')
        #vpc 查询vpc下是否有ecs资源
        cvms = Cvm.get_request(self)
        cvms_req = eval(cvms.replace('false', 'False'))['InstanceSet']
        if cvms_req:
            for cvm in cvms_req:
                if VpcId == cvm['VirtualPrivateCloud']['VpcId']:
                    return None
        # vpc 查询vpc下是否有clb资源
        clbs = Clb.get_request(self)
        clbs_req = eval(clbs.replace('false', 'False'))['LoadBalancerSet']
        if clbs_req:
            for clb in clbs_req:
                print(clb['VpcId'])
                if VpcId == clb['VpcId']:
                    return None
        return i

# @Vpc.action_registry.register('delete')
# class VpcDelete(MethodAction):
#
#     schema = type_schema('delete')
#     method_spec = {'op': 'delete'}
#
#     def get_request(self, vpc):
#         req = models.DeleteVpcRequest()
#         params = '{"VpcId" :"' + vpc["VpcId"] + '"}'
#         req.from_json_string(str(params))
#         Session.client(self, service).DeleteVpc(req)