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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.filters.filter import HuaweiRdsFilter
from c7n_huawei.filters.filter import MetricsFilter
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo
from huaweicloudsdkrds.v3 import *
from huaweicloudsdkcore.exceptions import exceptions

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

@Rds.filter_registry.register('Internet')
class HuaweiRdsFilter(HuaweiRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            - name: huawei-rds
              resource: huawei.rds
              filters:
                - type: Internet
    """

    schema = type_schema('Internet')

    def get_request(self, i):
        public_ips = i['public_ips']
        if len(public_ips) == 0:
            return None
        return i

@Rds.filter_registry.register('metrics')
class EcsMetricsFilter(MetricsFilter):
    # 云监控服务 CES https://support.huaweicloud.com/api-ces/ces_03_0033.html
    def get_request(self, dimensions):
        service = 'cloud_eye.rds'
        new_dimensions = []
        for dimension in dimensions:
            new_dimensions.append(
                {
                    "name": "rds_cluster_id",
                    "value": str(dimension['id'])
                })
        try:
            query = {
                "namespace": self.namespace,
                "metric_name": self.metric,
                "from": self.start,
                "to": self.end,
                "period": self.period,
                "filter": "average",
                "dimensions": new_dimensions
            }
            servers = Session.client(self, service).metric_aggregations(**query)
            arr = list()  # 创建 []
            if servers is not None:
                for server in servers:
                    json = dict()  # 创建 {}
                    json = Session._loads_(json, server)
                    arr.append(json)
        except Exception as err:
            pass
        return arr