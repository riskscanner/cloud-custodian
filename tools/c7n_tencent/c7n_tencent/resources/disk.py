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
from tencentcloud.cbs.v20170312 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentDiskFilter, TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'cbs_client.disk'

@resources.register('disk')
class Disk(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'cbs_client.disk'
        enum_spec = (None, 'DiskSet', None)
        id = 'DiskId'

    def get_request(self):
        offset = 0
        limit = 100
        res = []
        try:
            while 0 <= offset:
                req = models.DescribeDisksRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeDisks(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('DiskSet', eval(respose))
                res = res + result
                if len(result) == limit:
                    offset += 1
                else:
                    return res
                # 输出json格式的字符串回包
                # print(resp.to_json_string(indent=2))

                # 也可以取出单个值。
                # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
                # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            logging.error(err)
            return False
        return res

@Disk.filter_registry.register('unused')
class TencentDiskFilter(TencentDiskFilter):
    """Filters

       :Example:

       .. code-block:: yaml

policies:
 - name: tencent-orphaned-disk
   resource: tencent.disk
   filters:
     - type: unused
    """
    # 云盘状态。取值范围：
    # UNATTACHED：未挂载
    # ATTACHING：挂载中
    # ATTACHED：已挂载
    # DETACHING：解挂中
    # EXPANDING：扩容中
    # ROLLBACKING：回滚中
    # TORECYCLE：待回收
    # DUMPING：拷贝硬盘中。
    schema = type_schema('UNATTACHED')

@Disk.filter_registry.register('encrypt')
class encrypt(TencentFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下所有处于关联状态的磁盘均已加密，视为“合规”，否则视为“不合规”
            - name: tencent-disk-encrypt
              resource: tencent.disk
              filters:
                - type: encrypt
                  value: true
    """

    encrypt = "Encrypt"
    schema = type_schema(
        'encrypt',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        data = i[self.encrypt]
        if data == self.data.get('value', ''):
            return False
        return i

@Disk.action_registry.register('delete')
class DiskDelete(MethodAction):

    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_request(self, disk):
        req = models.TerminateDisksRequest()
        params = '{"DiskIds" :["' + disk["DiskId"] + '"]}'
        req.from_json_string(params)
        Session.client(self, service).TerminateDisks(req)

