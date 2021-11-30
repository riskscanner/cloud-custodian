import jmespath
from c7n_tencent import page, filter_util
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentFilter, TencentEsFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.es.v20180416 import es_client, models
import logging

from c7n.utils import type_schema

service = 'es_client.es'


@resources.register('es')
class Postgres(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'postgres_client.postgres'
        enum_spec = (None, 'InstanceList', None)
        id = 'InstanceId'

    def get_request(self):
        listField = self.resource_type.enum_spec[1]
        res = []
        try:
            req = models.DescribeInstancesRequest()
            client = Session.client(self, service)
            # 查询到所有分页数据
            resp = page.page_all(client.DescribeInstances, req, listField,
                                 'TotalCount')
            #  将结果转换为字典
            respose = resp.to_json_string().replace('null', 'None').replace('false', 'False').replace('true', 'True')
            res = jmespath.search(listField, eval(respose))
            # 也可以取出单个值。
            # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
        except TencentCloudSDKException as err:
            logging.error(err)
        return res


@Postgres.filter_registry.register('InstanceId')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'InstanceId',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('InstanceName')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'InstanceName',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('Region')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'Region',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('Zone')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'Zone',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('AppId')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'AppId',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('Uin')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'Uin',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('VpcUid')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'VpcUid',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('SubnetUid')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'SubnetUid',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('Status')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'Status',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('ChargeType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'ChargeType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('ChargePeriod')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'ChargePeriod',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('RenewFlag')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'RenewFlag',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('CpuNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'CpuNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('MemSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MemSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('DiskType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'DiskType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('DiskSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'DiskSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('EsDomain')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsDomain',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('EsVip')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsVip',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('EsPort')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsPort',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('KibanaUrl')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'KibanaUrl',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('EsVersion')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsVersion',
        **filter_util.get_schema('string'))


# @Postgres.filter_registry.register('EsConfig')
# class NetworkTypePostgresFilter(TencentEsFilter):
#     schema = type_schema(
#         'EsConfig',
#         **filter_util.get_schema('string'))
#

@Postgres.filter_registry.register('EsAcl.BlackIpList')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsAcl.BlackIpList',
        **filter_util.get_schema('list_string'))


@Postgres.filter_registry.register('EsAcl.WhiteIpList')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsAcl.WhiteIpList',
        **filter_util.get_schema('list_string'))


@Postgres.filter_registry.register('CreateTime')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'CreateTime',
        **filter_util.get_schema('time'))


@Postgres.filter_registry.register('UpdateTime')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'UpdateTime',
        **filter_util.get_schema('time'))


@Postgres.filter_registry.register('Deadline')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'Deadline',
        **filter_util.get_schema('time'))


@Postgres.filter_registry.register('InstanceType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'InstanceType',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('IkConfig.MainDict..Key')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig..MainDict.Key',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.MainDict..Name')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig..MainDict.Name',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.MainDict..Size')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig..MainDict.Size',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('IkConfig.Stopwords..Key')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig..Stopwords.Key',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.Stopwords..Name')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig..Stopwords.Name',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.Stopwords..Size')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.Stopwords..Size',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('IkConfig.QQDict..Key')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.QQDict..Key',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.QQDict..Name')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.QQDict..Name',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.QQDict..Size')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.QQDict..Size',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('IkConfig.Synonym..Key')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.Synonym..Key',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.Synonym..Name')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.Synonym..Name',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('IkConfig.Synonym..Size')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.Synonym..Size',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('IkConfig.UpdateType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'IkConfig.UpdateType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('MasterNodeInfo.EnableDedicatedMaster')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.UpdateType',
        **filter_util.get_schema('boolean'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeCpuNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeCpuNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeMemSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeMemSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeDiskSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeDiskSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('MasterNodeInfo.MasterNodeDiskType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MasterNodeInfo.MasterNodeDiskType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('CosBackup.IsAutoBackup')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'CosBackup.IsAutoBackup',
        **filter_util.get_schema('boolean'))


@Postgres.filter_registry.register('CosBackup.BackupTime')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'CosBackup.BackupTime',
        **filter_util.get_schema('time'))


@Postgres.filter_registry.register('AllowCosBackup')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'AllowCosBackup',
        **filter_util.get_schema('boolean'))


@Postgres.filter_registry.register('TagList')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'TagList',
        **filter_util.get_schema('list_string'))


@Postgres.filter_registry.register('LicenseType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'LicenseType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('EnableHotWarmMode')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EnableHotWarmMode',
        **filter_util.get_schema('boolean'))


@Postgres.filter_registry.register('WarmNodeType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmNodeType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('WarmNodeNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmNodeNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('WarmCpuNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmCpuNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('WarmMemSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmMemSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('WarmDiskType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmDiskType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('WarmDiskSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'WarmDiskSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..NodeNum')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..NodeNum',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..NodeType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..NodeType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeInfoList..Type')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..Type',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeInfoList..DiskType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..DiskType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeInfoList..DiskSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..DiskSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..LocalDiskInfo')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..LocalDiskInfo',
        **filter_util.get_schema('is_empty'))


@Postgres.filter_registry.register('NodeInfoList.LocalDiskInfo..LocalDiskType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList.LocalDiskInfo..LocalDiskType',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('NodeInfoList.LocalDiskInfo..LocalDiskSize')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList.LocalDiskInfo..LocalDiskSize',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList.LocalDiskInfo..LocalDiskCount')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList.LocalDiskInfo..LocalDiskCount',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..DiskCount')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..DiskCount',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..DiskEncrypt')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..DiskEncrypt',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('NodeInfoList..DiskEncrypt')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'NodeInfoList..DiskEncrypt',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('EsPublicUrl')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsPublicUrl',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('MultiZoneInfo..Zone')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MultiZoneInfo..Zone',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('MultiZoneInfo..SubnetId')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'MultiZoneInfo..SubnetId',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('DeployMode')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'DeployMode',
        **filter_util.get_schema('number'))


@Postgres.filter_registry.register('PublicAccess')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'PublicAccess',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('EsPublicAcl.BlackIpList')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsPublicAcl.BlackIpList',
        **filter_util.get_schema('list_string'))


@Postgres.filter_registry.register('EsPublicAcl.WhiteIpList')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'EsPublicAcl.BlackIpList',
        **filter_util.get_schema('list_string'))


@Postgres.filter_registry.register('KibanaPrivateUrl')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'KibanaPrivateUrl',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('KibanaPublicAccess')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'KibanaPublicAccess',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('KibanaPrivateAccess')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'KibanaPrivateAccess',
        **filter_util.get_schema('string'))


@Postgres.filter_registry.register('SecurityType')
class NetworkTypePostgresFilter(TencentEsFilter):
    schema = type_schema(
        'SecurityType',
        **filter_util.get_schema('number'))
