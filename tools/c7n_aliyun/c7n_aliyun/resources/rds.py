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
import os

from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from aliyunsdkrds.request.v20140815.DescribeAvailableZonesRequest import DescribeAvailableZonesRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstanceAttributeRequest import DescribeDBInstanceAttributeRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest

from c7n.utils import type_schema
from c7n_aliyun.client import Session
from c7n_aliyun.filters.filter import AliyunRdsFilter, MetricsFilter
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')

service = 'rds'
regionId = os.getenv('ALIYUN_DEFAULT_REGION')

@resources.register('rds')
class Rds(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'rds'
        enum_spec = (None, 'Items.DBInstance', None)
        id = 'DBInstanceId'

    def get_request(self):
        try:
            # clt = Session.client(self, service)
            # request = DescribeRegionsRequest()
            # request.set_accept_format('json')
            # response_str = clt.do_action_with_exception(request)
            # response = json.loads(response_str)
            """
                aliyunsdkcore.client:ERROR ServerException occurred. Host:location-readonly.aliyuncs.com SDK-Version:2.13.11 
                ServerException:HTTP Status: 404 Error:InvalidRegionId The specified region does not exist. 
                RequestID: 4B62B859-1CBD-46E9-9A41-A2F5FD672E2C
                用DescribeRegionsRequest去查,sdk直接会抛出ERROR异常，虽然不影响返回的数据，但是在安全合规模块遇到ERROR会报错。所以暂时写死region
            """
            if regionId == "cn-wulanchabu":
                flag = False
            else:
                flag = True
            # if response is not None:
            #     region_list = response.get('Regions').get('RDSRegion')
            #     for res in region_list:
            #         if regionId == res['RegionId']:
            #             flag = True
            #             break
        except Exception as error:
            logging.warn(error)
            flag = False
        if flag:
            # 乌兰察布暂时不支持rds
            return DescribeDBInstancesRequest()
        else:
            logging.warn("RDS service in %s is not supported!", regionId)
            return flag

@Rds.filter_registry.register('AvailableZones')
class AliyunRdsFilter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下RDS实例支持多可用区，视为“合规”。
            - name: aliyun-rds-availablezones
              resource: aliyun.rds
              filters:
                - type: AvailableZones
                  value: false
    """
    schema = type_schema(
        'AvailableZones',
        **{'value': {'type': 'boolean'}})
    filter = None

    def get_request(self, i):
        request = DescribeAvailableZonesRequest()
        request.set_accept_format('json')
        # 数据库类型。取值：
        # MySQL
        # SQLServer
        # PostgreSQL
        # PPAS
        # MariaDB
        request.set_Engine(i['Engine'])

        response = Session.client(self, service).do_action_with_exception(request)

        string = str(response, encoding="utf-8").replace("false", "False")
        data = eval(string)
        if self.data['value']==True:
            flag = len(data['AvailableZones']) > 0
        else:
            flag = len(data['AvailableZones']) < 0
        if flag != self.data['value']:
            return False
        return i

@Rds.filter_registry.register('normal')
class AliyunRdsFilter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            - name: aliyun-rds
              resource: aliyun.rds
              filters:
                - type: normal
    """
    # 白名单模式。取值：
    #
    # normal：通用模式
    # safety：高安全模式
    schema = type_schema('normal')
    filter = 'SecurityIPMode'

    def get_request(self, i):
        request = DescribeDBInstanceAttributeRequest()
        request.set_accept_format('json')

        request.set_DBInstanceId(i['DBInstanceId'])
        response = Session.client(self, service).do_action_with_exception(request)
        string = str(response, encoding="utf-8").replace("false", "False")
        data = eval(string)
        DBInstanceAttributes = data['Items']['DBInstanceAttribute']
        for obj in DBInstanceAttributes:
            if obj[self.filter] != self.data['type']:
                return False
        i['DBInstanceAttributes'] = DBInstanceAttributes
        return i

@Rds.filter_registry.register('HighAvailability')
class AliyunRds2Filter(AliyunRdsFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 账号下RDS实例具备高可用能力，视为“合规”，否则属于“不合规”。
            - name: aliyun-rds
              resource: aliyun.rds
              filters:
                - type: HighAvailability
    """
    # 实例系列，取值：
    #
    # Basic：基础版
    # HighAvailability：高可用版
    # AlwaysOn：集群版
    # Finance：三节点企业版
    schema = type_schema('Basic')
    filter = 'Category'

    def get_request(self, i):
        request = DescribeDBInstanceAttributeRequest()
        request.set_accept_format('json')

        request.set_DBInstanceId(i['DBInstanceId'])
        response = Session.client(self, service).do_action_with_exception(request)
        string = str(response, encoding="utf-8").replace("false", "False")
        data = eval(string)
        DBInstanceAttributes = data['Items']['DBInstanceAttribute']
        for obj in DBInstanceAttributes:
            if obj[self.filter] != self.data['type']:
                return False
        i['DBInstanceAttributes'] = DBInstanceAttributes
        return i

@Rds.filter_registry.register('metrics')
class RdsMetricsFilter(MetricsFilter):

    """
          1 policies:
          2   - name: aliyun-rds
          3     resource: aliyun.rds
          4     filters:
          6       - type: metrics
          7         name: IOPSUsage
          9         startTime: '2020-11-02T08:00Z'
         10         endTime: '2020-11-08T08:00Z'
         11         statistics: Average
         12         value: 30000
         13         op: less-than
    """

    # IOPS使用率:IOPSUsage
    # 连接数使用率: ConnectionUsage
    # 内存使用率: MemoryUsage
    # CPU使用率: CpuUsage
    def get_request(self, rds):
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_StartTime(self.start)
        request.set_Period(self.period)
        request.set_Namespace(self.namespace)
        request.set_MetricName(self.metric)
        return request