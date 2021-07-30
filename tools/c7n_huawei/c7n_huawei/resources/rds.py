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

import urllib3
from huaweicloudsdkces.v1 import *
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkrds.v3 import *

from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiRdsFilter
from c7n_huawei.filters.filter import MetricsFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'rds'

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rds'
        enum_spec = (None, 'instances', None)
        id = 'id'

    def get_request(self):
        try:
            request = ListInstancesRequest()
            response = Session.client(self, service).list_instances(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response

@Rds.filter_registry.register('internet')
class HuaweiRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            - name: huawei-rds-internet
              resource: huawei.rds
              filters:
                - type: internet
    """

    schema = type_schema('internet')

    def get_request(self, i):
        if i['public_ips'] is None:
            return None
        public_ips = i['public_ips']
        if len(public_ips) == 0:
            return None
        return i

@Rds.filter_registry.register('metrics')
class EcsMetricsFilter(MetricsFilter):
    # 云监控服务 CES https://support.huaweicloud.com/api-ces/ces_03_0033.html
    # https://apiexplorer.developer.huaweicloud.com/apiexplorer/sdk?product=CES&api=BatchListMetricData
    def get_request(self, dimensions):
        request = BatchListMetricDataRequest()
        service = 'ces'
        new_dimensions = []
        for dimension in dimensions:
            new_dimensions.append(
                {
                    "name": "rds_cluster_id",
                    "value": str(dimension['id'])
                })
        try:
            listMetricsDimensionDimensionsMetrics = []
            for dimension in dimensions:
                listMetricsDimensionDimensionsMetrics.append(
                    MetricsDimension(
                        name="rds_cluster_id",
                        value=str(dimension['id'])
                    )
               )
            listMetricInfoMetricsbody = [
                MetricInfo(
                    namespace=self.namespace,
                    metric_name=self.metric,
                    dimensions=listMetricsDimensionDimensionsMetrics
                )
            ]
            request.body = BatchListMetricDataRequestBody(
                to=self.end,
                _from=self.start,
                filter=self.statistics,
                period=self.period,
                metrics=listMetricInfoMetricsbody
            )
            response = Session.client(self, service).batch_list_metric_data(request)
        except Exception as err:
            pass
        return response

@Rds.filter_registry.register('internet-access')
class InternetAccessRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下RDS实例不允许任意来源公网访问，视为“合规”
            - name: huawei-rds-internet-access
              resource: huawei.rds
              filters:
                - type: internet-access
                  value: true
    """
    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        public_ips = i['public_ips']
        if self.data['value'] == True:
            if len(public_ips) == 0:
                return None
            return i
        else:
            if len(public_ips) > 0:
                return None
            return i

@Rds.filter_registry.register('high-availability')
class HighAvailabilityRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下RDS实例具备高可用能力，视为“合规”，否则属于“不合规”。
            - name: huawei-rds-high-availability
              resource: huawei.rds
              filters:
                - type: high-availability
    """
    # 实例类型,取值为“Single”,“Ha”或“Replica”,分别对应于单机实例、主备实例、只读实例。
    filter = 'type'

    def get_request(self, i):
        if i[self.filter] != 'Ha':
            return i
        return False

@Rds.filter_registry.register('storagefull')
class HighAvailabilityRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下RDS实例磁盘空间是否已满，未满视为“合规”，否则属于“不合规”。
            - name: huawei-rds-storagefull
              resource: huawei.rds
              filters:
                - type: storagefull
    """
    filter = 'status'

    def get_request(self, i):
        if i[self.filter] == 'STORAGE FULL':
            return i
        return False

@Rds.filter_registry.register('instance-network-type')
class InstanceNetworkTypeRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测您账号下的Redis实例是否运行在VPC网络环境下。
            - name: huawei-rds-instance-network-type
              resource: huawei.rds
              filters:
                - type: instance-network-type
                  value: VPC
    """
    # 实例的网络类型，取值：
    #
    # VPC：VPC网络
    schema = type_schema(
        'instance-network-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if i['vpc_id'] is not None:
            return False
        return i

@Rds.filter_registry.register('charge-info')
class InstanceNetworkTypeRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
           #测您账号下RDS数据库实例计费类型信息，按需视为“合规”，否则视为“不合规”
            - name: huawei-rds-charge-info
              resource: huawei.rds
              filters:
                - type: charge-info
                  value: postPaid
    """
    # prePaid:预付费,即包年/包月。
    # postPaid:后付费,即按需付费。
    schema = type_schema(
        'charge-info',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if i['charge_info']['charge_mode'] == self.data['value']:
            return False
        return i