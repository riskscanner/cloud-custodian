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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo
from c7n_huawei.filters.filter import HuaweiRdsFilter
from c7n_huawei.filters.filter import MetricsFilter

service = 'rdsv3.rds'

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rdsv3.rds'
        enum_spec = (None, None, None)
        id = 'id'
        dimension = 'id'

    def get_request(self):
        query = {
            'offset': 0,
            'limit': 100
        }
        try:
            rds = Session.client(self, service).instances(**query)
            arr = list()  # 创建 []
            if rds is not None:
                for rd in rds:
                    json = dict()  # 创建 {}
                    json = Session._loads_(json, rd)
                    arr.append(json)
        except Exception as err:
            pass
        return arr

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

@Rds.action_registry.register('delete')
class RdsDelete(MethodAction):
    """
        policies:
          - name: huawei-rds-delete
            resource: huawei.rds
            actions:
              - delete
    """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}

    def get_request(self, rds):
        Session.client(self, service).delete_security_group(rds['id'])