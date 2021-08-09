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
import operator

import jmespath
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.cvm.v20170312 import models

from c7n.utils import type_schema
from c7n_tencent.actions import MethodAction
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import MetricsFilter
from c7n_tencent.filters.filter import TencentAgeFilter, TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'cvm_client.cvm'

@resources.register('cvm')
class Cvm(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'cvm_client.cvm'
        namespace = 'QCE/CVM'
        enum_spec = (None, 'InstanceSet', None)
        id = 'InstanceId'
        dimension = 'InstanceId'

    def get_request(self):
        offset = 0
        limit = 100
        res = []
        try:
            while 0 <= offset:
                # 实例化一个cvm实例信息查询请求对象,每个接口都会对应一个request对象。
                req = models.DescribeInstancesRequest()
                params = {
                    "Offset": offset,
                    "Limit": limit
                }
                req.from_json_string(json.dumps(params))
                # 通过client对象调用DescribeInstances方法发起请求。注意请求方法名与请求对象是对应的。
                # 返回的resp是一个DescribeInstancesResponse类的实例，与请求对象对应。
                resp = Session.client(self, service).DescribeInstances(req)
                respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
                result = jmespath.search('InstanceSet', eval(respose))
                res = res + result
                if len(result) == limit:
                    offset += 1
                else:
                    return res
                # 输出json格式的字符串回包
                # print(resp.to_json_string(indent=2))

                # 也可以取出单个值。
                # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
                # print(resp.InstanceSet)
                # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            logging.error(err)
            return False
        return res

@Cvm.filter_registry.register('metrics')
class CvmMetricsFilter(MetricsFilter):

    def get_request(self):
        from tencentcloud.monitor.v20180724 import models
        try:
            req = models.GetMonitorDataRequest()
            return req
        except TencentCloudSDKException as err:
            logging.error(err)
        return None

@Cvm.filter_registry.register('instance-age')
class CvmAgeFilter(TencentAgeFilter):
    """Filters instances based on their age (in days)
        policies:
          - name: tencent-cvm-30-days-plus
            resource: tencent.cvm
            filters:
              - type: instance-age
                op: lt
                days: 30
    """

    date_attribute = "CreatedTime"
    ebs_key_func = operator.itemgetter('CreatedTime')

    schema = type_schema(
        'instance-age',
        op={'$ref': '#/definitions/filters_common/comparison_operators'},
        days={'type': 'number'},
        hours={'type': 'number'},
        minutes={'type': 'number'})

    def get_resource_date(self, i):
        # '2019-11-20T08:21:02Z'
        return i.get('CreatedTime', '2021-08-10T08:21:02Z')

@Cvm.action_registry.register('start')
class Start(MethodAction):
    """
        policies:
          - name: tencent-cvm-start
            resource: tencent.cvm
            actions:
              - start
    """

    schema = type_schema('start')
    method_spec = {'op': 'start'}
    attr_filter = ('status', ('SHUTOFF',))

    def get_request(self, instance):
        req = models.StartInstancesRequest()
        params = '{"InstanceId" :"' + instance["InstanceId"] + '"}'
        req.from_json_string(params)
        resp = Session.client(self, service).StartInstances(req)
        return resp.to_json_string().replace('null', 'None')

@Cvm.action_registry.register('stop')
class Stop(MethodAction):
    """
        policies:
          - name: tencent-cvm-stop
            resource: tencent.cvm
            actions:
              - stop
    """
    schema = type_schema('stop')
    method_spec = {'op': 'stop'}
    attr_filter = ('status', ('ACTIVE',))

    def get_request(self, instance):
        req = models.StopInstancesRequest()
        params = '{"InstanceId" :"' + instance["InstanceId"] + '"}'
        req.from_json_string(params)
        resp = Session.client(self, service).StopInstances(req)
        return resp.to_json_string().replace('null', 'None')


@Cvm.action_registry.register('delete')
class Delete(MethodAction):
    """
        policies:
          - name: tencent-cvm-delete
            resource: tencent.cvm
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}
    attr_filter = ('status', ('SHUTOFF',))

    def get_request(self, instance):
        req = models.TerminateInstancesRequest()
        params = '{"InstanceId" :"' + instance["InstanceId"] + '"}'
        req.from_json_string(params)
        Session.client(self, service).TerminateInstances(req)

@Cvm.filter_registry.register('public-ip-address')
class PublicIpAddress(TencentFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # CVM实例未直接绑定公网IP，视为“合规”。该规则仅适用于 IPv4 协议
            - name: tencent-cvm-public-ip-address
              resource: tencent.cvm
              filters:
                - type: public-ip-address
    """
    public_ip_address = "PublicIpAddresses"
    schema = type_schema('public-ip-address')

    def get_request(self, i):
        data = i[self.public_ip_address]
        if data is None or len(data) == 0:
            return False
        return i

@Cvm.filter_registry.register('stop-charging-mode')
class StopChargingMode(TencentFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # CVM实例的关机计费模式是否为关机停止收费，是视为“合规”，否则视为“不合规”
            - name: tencent-cvm-stop-charging-mode
              resource: tencent.cvm
              filters:
                - type: stop-charging-mode
                  value: STOP_CHARGING
    """

    # 实例的关机计费模式。
    # 取值范围：
    # KEEP_CHARGING：关机继续收费
    # STOP_CHARGING：关机停止收费
    # NOT_APPLICABLE：实例处于非关机状态或者不适用关机停止计费的条件

    stop_charging_mode = "StopChargingMode"
    schema = type_schema(
        'stop-charging-mode',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        data = i[self.stop_charging_mode]
        if data == self.data.get('value', ''):
            return False
        return i
