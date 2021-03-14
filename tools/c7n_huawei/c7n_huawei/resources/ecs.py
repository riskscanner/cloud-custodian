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

import jmespath
import urllib3
from huaweicloudsdkces.v1 import *
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkecs.v2 import *

from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiAgeFilter, HuaweiEcsFilter, MetricsFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
service = 'ecs'

@resources.register('ecs')
class Ecs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'ecs'
        enum_spec = (None, 'servers', None)
        id = 'id'
        dimension = 'id'

    def get_request(self):
        try:
            request = ListServersDetailsRequest()
            response = Session.client(self, service).list_servers_details(request)
        except exceptions.ClientRequestException as e:
            logging.error(e.status_code, e.request_id, e.error_code, e.error_msg)
        return response


@Ecs.filter_registry.register('public-ip-address')
class PublicIpAddress(HuaweiEcsFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # ECS实例未直接绑定公网IP，视为“合规”。该规则仅适用于 IPv4 协议
            - name: huawei-ecs-public-ipaddress
              resource: huawei.ecs
              filters:
                - type: public-ip-address
    """
    # fixed 内网
    # floating 公网

    public_ip_address = "addresses"
    schema = type_schema('public-ip-address')

    def get_request(self, i):
        data = jmespath.search(self.public_ip_address, i)
        if len(data) == 0:
            return False
        else:
            for addrs in list(data.values()):
                for addr in addrs:
                    if addr['os_ext_ip_stype'] == 'floating':
                        return i
        return False


@Ecs.filter_registry.register('instance-age')
class EcsAgeFilter(HuaweiAgeFilter):
    """Filters instances based on their age (in days)
        policies:
          - name: huawei-ecs-instance-age
            resource: huawei.ecs
            filters:
              - type: instance-age
                op: lt
                days: 30
    """

    date_attribute = "os_srv_us_glaunched_at"

    schema = type_schema(
        'instance-age',
        op={'$ref': '#/definitions/filters_common/comparison_operators'},
        days={'type': 'number'},
        hours={'type': 'number'},
        minutes={'type': 'number'})

    def get_resource_date(self, i):
        # '2020-07-27T05:55:32.000000'
        return i['os_srv_us_glaunched_at']

@Ecs.filter_registry.register('instance-network-type')
class InstanceNetworkTypeEcsFilter(HuaweiEcsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下所有ECS实例已关联到VPC；若您配置阈值，则关联的VpcId需存在您列出的阈值中，视为“合规”
            - name: huawei-ecs-instance-network-type
              resource: huawei.ecs
              filters:
                - type: instance-network-type
                  value: vpc
    """
    schema = type_schema(
        'instance-network-type',
        **{'value': {'type': 'string'}})

    def get_request(self, i):
        if self.data['value'] == 'vpc':
            if i['metadata']['vpc_id'] is not None:
                return False
        return i

@Ecs.filter_registry.register('metrics')
class EcsMetricsFilter(MetricsFilter):

    """Filters
       :Example:
       .. code-block:: yaml

        policies:
          #Huawei CPU使用率扫描(每86700秒扫描7天内cpu平均值小于30)
          - name: huawei-ecs-underutilized
            resource: huawei.ecs
            filters:
              - type: metrics
                name: CPUUtilization
                days: 7
                period: 86700
                statistics: Average
                value: 30
                op: less-than
    """

    def get_request(self, dimensions):
        request = BatchListMetricDataRequest()
        listMetricsDimensionDimensionsMetrics= [
            MetricsDimension(
                name="instance_id",
                value=dimensions[0]['id']
            )
        ]
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
            period=str(self.period),
            metrics=listMetricInfoMetricsbody
        )

        try:
            response = Session.client(self, "ces").batch_list_metric_data(request)
        except Exception as err:
            pass
        return response