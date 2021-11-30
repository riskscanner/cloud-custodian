import jmespath
from c7n_tencent import page
from c7n_tencent.query import QueryResourceManager, TypeInfo
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import logging
from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentFilter
from c7n_tencent.provider import resources
from tencentcloud.postgres.v20170312 import models

service = 'postgres_client.postgres'


@resources.register('postgres')
class Postgres(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'postgres_client.postgres'
        enum_spec = (None, 'DBInstanceSet', None)
        id = 'DBInstanceId'

    def get_request(self):
        res = []
        try:
            req = models.DescribeDBInstancesRequest()
            client = Session.client(service)
            # 查询到所有分页数据
            resp = page.page_all(client.DescribeDBInstances, req, 'DBInstanceSet',
                                 'TotalCount')
            #  将结果转换为字典
            respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
            res = jmespath.search('DBInstanceSet', eval(respose))
            # 也可以取出单个值。
            # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
        except TencentCloudSDKException as err:
            logging.error(err)
        return res


@Postgres.filter_registry.register('network-type')
class NetworkTypePostgresFilter(TencentFilter):
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


def network_is_public(obj):
    return obj and obj['NetType'] and obj['NetType'] == 'public' and obj['Status'] and obj['Status'] == 'opened'


@Postgres.filter_registry.register('internet-access')
class InternetAccessTypePostgresFilter(TencentFilter):
    schema = type_schema(
        'internet-access',
        **{'value': {'type': 'boolean'}})

    """
         Filters
         :Example:
         .. code-block:: yaml

          policies:
              # 检测您账号下postgres实例不允许任意来源公网访问，视为“合规”
              - name: tencent-postgres-internet-access
                resource: tencent.postgres
                filters:    
                  - type: internet-access
                    value: true
      """

    def get_request(self, i):
        if self.data.get('value', ''):
            if len(list(filter(network_is_public, i['DBInstanceNetInfo']))) > 0:
                return i
            else:
                return False
        else:
            if len(list(filter(network_is_public, i['DBInstanceNetInfo']))) == 0:
                return i
            else:
                return False
