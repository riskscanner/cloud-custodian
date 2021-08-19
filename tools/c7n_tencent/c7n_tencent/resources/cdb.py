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
from tencentcloud.cdb.v20170320 import models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentCdbFilter, TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'cdb_client.cdb'

@resources.register('cdb')
class Cdb(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'cdb_client.cdb'
        enum_spec = (None, 'Items', None)
        id = 'InstanceId'

    def get_request(self):
        offset = 0
        limit = 20
        res = []
        try:
            while 0 <= offset:
                req = models.DescribeDBInstancesRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                resp = Session.client(self, service).DescribeDBInstances(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('Items', eval(respose))
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

@Cdb.filter_registry.register('Internet')
class TencentCdbFilter(TencentCdbFilter):
    """Filters

       :Example:

       .. code-block:: yaml

           policies:
             - name: tencent-running-cdb
               resource: tencent.cdb
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


@Cdb.filter_registry.register('internet-access')
class InternetAccessCdbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下CDB实例不允许任意来源公网访问，视为“合规”
            - name: tencent-cdb-internet-access
              resource: tencent.cdb
              filters:
                - type: internet-access
                  value: true
    """
    # 外网状态，可能的返回值为：0 - 未开通外网；1 - 已开通外网；2 - 已关闭外网

    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        if self.data.get('value', ''):
            if i.get('WanStatus', '') == 1:
                return i
        else:
            if i.get('WanStatus', '') != 1:
                return i
        return False

@Cdb.filter_registry.register('device-type')
class DeviceTypeCdbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下CDB实例具备高可用能力，视为“合规”，否则属于“不合规”。
            - name: tencent-cdb-device-type
              resource: tencent.cdb
              filters:
                - type: device-type
                  value: BASIC
    """

    schema = type_schema(
        'device-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if i.get('DeviceType', '') == self.data.get('value', ''):
            return i
        return False


@Cdb.filter_registry.register('availablezones')
class AvailablezonesCdbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下CDB实例支持多可用区，视为“合规”。
            - name: tencent-cdb-availablezones
              resource: tencent.cdb
              filters:
                - type: availablezones
                  value: true
    """
    # 可用区部署方式。可能的值为：0 - 单可用区；1 - 多可用区
    schema = type_schema(
        'availablezones',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        if self.data.get('value', ''):
            if i.get('DeployMode', '') == 1:
                return i
            return False
        else:
            if i.get('DeployMode', '') != 1:
                return i
            return False

@Cdb.filter_registry.register('network-type')
class NetworkTypeCdbFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下CDB实例已关联到VPC；若您配置阈值，则关联的VpcId需存在您列出的阈值中，视为“合规”。
            - name: tencent-cdb-instance-network-type
              resource: tencent.cdb
              filters:
                - type: network-type
                  value: vpc
    """
    schema = type_schema(
        'network-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if self.data.get('value', '') == "vpc":
            if i.get('VpcId', ''):
                return False
            return i
        else:
            if i.get('VpcId', ''):
                return i
            return False


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

    def get_request(self, cdb):
        req = models.RestartDBInstancesRequest()
        params = '{"ItemId" :"' + cdb["ItemId"] + '"}'
        req.from_json_string(params)
        Session.client(self, service).RestartDBInstances(req)
