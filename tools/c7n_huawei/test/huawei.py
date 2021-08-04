import logging

import jmespath
import urllib3
from huaweicloudsdkces.v1 import *
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkecs.v2 import *
from huaweicloudsdkeip.v2 import *
from huaweicloudsdkelb.v2 import *
from huaweicloudsdkevs.v2 import *
from huaweicloudsdkvpc.v2 import *
from huaweicloudsdkrds.v3 import *
from huaweicloudsdkrds.v3.region.rds_region import RdsRegion
from huaweicloudsdkvpc.v2.region.vpc_region import VpcRegion
from huaweicloudsdkces.v1.region.ces_region import CesRegion
from huaweicloudsdkdds.v3 import *
from huaweicloudsdkdds.v3.region.dds_region import DdsRegion
from huaweicloudsdkdcs.v2 import *
from huaweicloudsdkdcs.v2.region.dcs_region import DcsRegion
from huaweicloudsdkiam.v3 import *
from huaweicloudsdkiam.v3.region.iam_region import IamRegion
from obs import ObsClient
from huaweicloudsdkcore.auth.credentials import GlobalCredentials

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/huawei.txt")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "huawei.ak" in line:
            ak = line[line.rfind('=') + 1:]
            json['ak'] = ak
        if "huawei.sk" in line:
            sk = line[line.rfind('=') + 1:]
            json['sk'] = sk
        if "huawei.project_id" in line:
            project_id = line[line.rfind('=') + 1:]
            json['project_id'] = project_id
        # if "huawei.domain_id" in line:
        #     domain_id = line[line.rfind('=') + 1:]
        #     json['domain_id'] = domain_id
    f.close()
    print('认证信息:   ' + str(json))
    return json


params = _loadFile_()

config = HttpConfig.get_default_config()
config.ignore_ssl_verification = True
config.timeout = 3
credentials = BasicCredentials(params['ak'], params['sk'], params['project_id'])
endpoint = "https://iam.myhuaweicloud.com/v3"

iam_credentials = GlobalCredentials(params['ak'], params['sk']) \

# 创建ObsClient实例
obsClient = ObsClient(
    access_key_id=params['ak'],
    secret_access_key=params['sk'],
    server="obs.cn-north-4.myhuaweicloud.com"
)

# 关闭obsClient
def closeObsClient():
    obsClient.close()

vpc_client = VpcClient.new_builder(VpcClient) \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint(endpoint) \
        .build()

ecs_client = EcsClient.new_builder(EcsClient) \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint("https://ecs.cn-north-4.myhuaweicloud.com") \
        .build()

ces_client = CesClient.new_builder(CesClient) \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint("https://ces.cn-north-4.myhuaweicloud.com") \
        .build()

evs_client = EvsClient.new_builder(EvsClient) \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint("https://evs.cn-north-4.myhuaweicloud.com") \
        .build()

eip_client = EipClient.new_builder(EipClient) \
        .with_http_config(config) \
        .with_credentials(credentials) \
        .with_endpoint("https://vpc.cn-north-4.myhuaweicloud.com") \
        .build()

elb_client = ElbClient.new_builder(ElbClient) \
    .with_http_config(config) \
    .with_credentials(credentials) \
    .with_endpoint("https://elb.cn-north-4.myhuaweicloud.com") \
    .build()

sg_client = VpcClient.new_builder() \
    .with_credentials(credentials) \
    .with_region(VpcRegion.value_of("cn-north-4")) \
    .build()

rds_client = RdsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(RdsRegion.value_of("cn-north-4")) \
        .build()

redis_client = DcsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(DcsRegion.value_of("cn-north-4")) \
        .build()

iam_client = IamClient.new_builder() \
        .with_credentials(iam_credentials) \
        .with_region(IamRegion.value_of("cn-north-4")) \
        .build()

dds_client = DdsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(DdsRegion.value_of("cn-north-4")) \
        .build()

def list_obs():
    try:
        # 列举桶
        resp = obsClient.listBuckets(isQueryLocation=True)
        if resp.status < 300:
            arrs = list()
            # 操作成功
            # 处理操作成功后业务逻辑
            for bucket in resp.body.buckets:
                if "cn-north-4" != bucket.location:
                    arrs.append(bucket)
                else:
                    # 列举对象
                    res = obsClient.listObjects(bucket.name)
                    if res.status < 300:
                        bucket['contents'] = res.body.contents
                    else:
                        bucket['contents'] = []
            for arr in arrs:
                resp.body.buckets.remove(arr)
            print(resp)
        else:
            # 操作失败，获取详细异常信息
            print(resp.errorMessage)
    except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)
    finally:
        # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
        # ObsClient在调用ObsClient.close方法关闭后不能再次使用
        closeObsClient()

def list_iam():
    try:
        request = ListUserLoginProtectsRequest()
        response = iam_client.list_user_login_protects(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_dds():
    try:
        request = ListInstancesRequest()
        response = dds_client.list_instances(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_redis():
    try:
        request = ListInstancesRequest()
        response = redis_client.list_instances(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_cdn():
    try:
        print("666")
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_rds():
    try:
        request = ListInstancesRequest()
        response = rds_client.list_instances(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_vpc():
    try:
        request = ListVpcsRequest()
        response = vpc_client.list_vpcs(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_sg():
    try:
        request = ListSecurityGroupsRequest()
        response = sg_client.list_security_groups(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_ecs():
    try:
        request = ListServersDetailsRequest()
        response = ecs_client.list_servers_details(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_ces():
    try:
        request = ListMetricsRequest()
        response = ces_client.list_metrics(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_evs():
    try:
        request = ListVolumesRequest()
        response = evs_client.list_volumes(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_eip():
    try:
        request = ListPublicipsRequest()
        response = eip_client.list_publicips(request)
        # print(response.publicips)
        print(type(eval(str(response))))
        print(jmespath.search("publicips", eval(str(response))))

    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_eip_bandwidths():
    try:
        request = ListBandwidthsRequest()
        response = eip_client.list_bandwidths(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

def list_elb():
    try:
        request = ListLoadbalancersRequest()
        response = elb_client.list_loadbalancers(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

if __name__ == '__main__':
    logging.info("Hello Huawei OpenApi!")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # list_vpc()
    # list_ecs()
    # list_ces()
    # list_evs()
    # list_eip()
    # list_eip_bandwidths()
    # list_elb()
    # list_sg()
    # list_rds()
    # list_cdn()
    # list_iam()
    # list_obs()
    # list_redis()