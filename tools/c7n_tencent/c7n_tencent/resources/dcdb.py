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
from tencentcloud.dcdb.v20180411 import models

from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentCdbFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'dcdb_client.dcdb'

@resources.register('dcdb')
class Dcdb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'dcdb_client.dcdb'
        enum_spec = (None, 'Instances', None)
        id = 'InstancesId'

    def get_request(self):
        offset = 0
        limit = 20
        res = []
        try:
            while 0 <= offset:
                req = models.DescribeDCDBInstancesRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeDCDBInstances(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('Instances', eval(respose))
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

@Dcdb.filter_registry.register('Internet')
class TencentDcdbFilter(TencentCdbFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
             - name: tencent-running-dcdb
               resource: tencent.dcdb
               filters:
                 - type: Internet
    """
    # 实例状态。取值范围：
    # 1：申请中
    # 2：运行中
    # 3：受限运行中(主备切换中)
    # 4：已隔离
    # 5：回收中
    # 6：已回收
    # 7：任务执行中(实例做备份、回档等操作)
    # 8：已下线
    # 9：实例扩容中
    # 10：实例迁移中
    # 11：只读
    # 12：重启中
    run_schema = 'running'
    # 外网状态，可能的返回值为：0-未开通外网；1-已开通外网(Internet)；2-已关闭外网
    schema = type_schema('Internet')