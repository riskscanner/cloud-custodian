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

from tencentcloud.cdb.v20170320 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentCdbFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'cdb_client.cdb'

@resources.register('cdb')
class Cdb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'cdb_client.cdb'
        enum_spec = (None, 'Items', None)
        id = 'ItemId'

    def get_requst(self):
        try:
            req = models.DescribeDBInstancesRequest()
            resp = Session.client(self, service).DescribeDBInstances(req)
            # 输出json格式的字符串回包
            # print(resp.to_json_string(indent=2))

            # 也可以取出单个值。
            # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
            # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            import traceback
            # 发生异常，打印异常堆栈
            logging.error(err)
            return traceback.format_exc()
        # tencent 返回的json里居然不是None，而是java的null，活久见
        return resp.to_json_string().replace('null', 'None')

@Cdb.filter_registry.register('running')
class TencentCdbFilter(TencentCdbFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
             - name: tencent-running-cdb
               resource: tencent.cdb
               filters:
                 - type: running
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
    schema = type_schema(2)

@Cdb.action_registry.register('restart')
class CdbReStart(MethodAction):
    """
        policies:
          - name: tencent-cdb-restart
            resource: tencent.cvm
            actions:
              - restart
    """

    schema = type_schema('restart')
    method_spec = {'op': 'restart'}
    attr_filter = ('status', ('SHUTOFF',))

    def get_requst(self, cdb):
        req = models.RestartDBInstancesRequest()
        params = {"ItemId": cdb['ItemId']}
        req.from_json_string(params)
        resp = Session.client(self, service).RestartDBInstances(req)
        return resp.to_json_string().replace('null', 'None')
