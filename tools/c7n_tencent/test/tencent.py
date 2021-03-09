import json
import logging

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tencentcloud.cbs.v20170312 import cbs_client, models
from tencentcloud.cdb.v20170320 import cdb_client, models
from tencentcloud.clb.v20180317 import clb_client, models
# -*- coding: utf-8 -*-
from tencentcloud.common import credential
# 导入对应产品模块的 client models。
from tencentcloud.monitor.v20180724 import monitor_client, models
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.dcdb.v20180411 import dcdb_client, models
from tencentcloud.vpc.v20170312 import vpc_client, models


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/tencent.txt")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "tencent.secret2Id" in line:
            secretId = line[line.rfind('=') + 1:]
            json['secretId'] = secretId
        if "tencent.secret2Key" in line:
            secretKey = line[line.rfind('=') + 1:]
            json['secretKey'] = secretKey
        if "tencent.endpoint" in line:
            endpoint = line[line.rfind('=') + 1:]
            json['endpoint'] = endpoint
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()

regionUU = 'ap-guangzhou'

# 实例化一个认证对象，入参需要传入腾讯云账户 secretId，secretKey
cred = credential.Credential(params['secretId'], params['secretKey'])

# 实例化要请求产品 (以 cvm 为例) 的 client 对象
client = cvm_client.CvmClient(cred, regionUU)

CbsClient = cbs_client.CbsClient(cred, regionUU)

vpcClient = vpc_client.VpcClient(cred, regionUU)

clbClient = clb_client.ClbClient(cred, regionUU)

cdbClient = cdb_client.CdbClient(cred, regionUU)

dcdbClient = dcdb_client.DcdbClient(cred, regionUU)

monitorClient = monitor_client.MonitorClient(cred, regionUU)

# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
endpoint = 'cos.' + regionUU + '.myqcloud.com'
config = CosConfig(Region=regionUU, SecretId=params['secretId'], SecretKey=params['secretKey'], Endpoint=endpoint)
# 2. 获取客户端对象
cosClient = CosS3Client(config)

def DescribeZonesRequest():
    # 实例化一个请求对象
    req = models.DescribeZonesRequest()
    # 通过 client 对象调用想要访问的接口，需要传入请求对象
    resp = client.DescribeZones(req)
    # 输出 json 格式的字符串回包
    print(resp.to_json_string())

def DescribeInstances():
    # 实例化一个 cvm 实例信息查询请求对象,每个接口都会对应一个 request 对象。
    req = models.DescribeInstancesRequest()

    # 填充请求参数,这里 request 对象的成员变量即对应接口的入参。
    # 您可以通过官网接口文档或跳转到 request 对象的定义处查看请求参数的定义。
    respFilter = models.Filter()  # 创建 Filter 对象, 以 zone 的维度来查询 cvm 实例。
    respFilter.Name = "zone"
    respFilter.Values = ["ap-shanghai-1", "ap-shanghai-2"]
    req.Filters = [respFilter]  # Filters 是成员为 Filter 对象的列表

    # 这里还支持以标准 json 格式的 string 来赋值请求参数的方式。下面的代码跟上面的参数赋值是等效的。
    params = '''{
            "Filters": [
                {
                    "Name": "zone",
                    "Values": ["ap-shanghai-1", "ap-shanghai-2"]
                }
            ]
        }'''
    req.from_json_string(params)

    # 通过 client 对象调用 DescribeInstances 方法发起请求。注意请求方法名与请求对象是对应的。
    # 返回的 resp 是一个 DescribeInstancesResponse 类的实例，与请求对象对应。
    resp = client.DescribeInstances(req)
    print(client)
    # 输出 json 格式的字符串回包
    print(resp.to_json_string(indent=2))

    # 也可以取出单个值。
    # 您可以通过官网接口文档或跳转到 response 对象的定义处查看返回字段的定义。
    print(resp.TotalCount)

def DescribeImages():
    req = models.DescribeImagesRequest()
    params = '{}'
    req.from_json_string(params)

    resp = client.DescribeImages(req)
    print(resp.to_json_string())

def DescribeDisks():
    req = models.DescribeDisksRequest()
    params = '{}'
    req.from_json_string(params)

    resp = CbsClient.DescribeDisks(req)
    print(resp.to_json_string())

def DescribeVpcsResponse():
    req = models.DescribeVpcsRequest()
    params = '{}'
    req.from_json_string(params)

    resp = vpcClient.DescribeVpcs(req)
    print(resp.to_json_string())

def DescribeAddresses():
    req = models.DescribeAddressesRequest()
    params = '{}'
    req.from_json_string(params)

    resp = vpcClient.DescribeAddresses(req)
    print(resp.to_json_string())

def DescribeSecurityGroups():
    req = models.DescribeSecurityGroupsRequest()
    params = '{}'
    req.from_json_string(params)

    resp = vpcClient.DescribeSecurityGroups(req)
    print(type(resp.SecurityGroupSet))
    for res in resp.SecurityGroupSet:
        print(type(res))
        print(res)
        req2 = models.DescribeSecurityGroupPoliciesRequest()
        params = '{"SecurityGroupId":"' + res.SecurityGroupId + '"}'
        req2.from_json_string(params)
        resp2 = vpcClient.DescribeSecurityGroupPolicies(req2)
        res.IpPermissions = resp2.SecurityGroupPolicySet

    print(resp.to_json_string())

def DescribeLoadBalancers():
    from tencentcloud.clb.v20180317 import models
    req = models.DescribeLoadBalancersRequest()
    params = '{}'
    req.from_json_string(params)

    resp = clbClient.DescribeLoadBalancers(req)
    print(resp.to_json_string())

def DescribeTargetsResponse():
    from tencentcloud.clb.v20180317 import models
    req = models.DescribeTargetsRequest()
    params ='{"LoadBalancerId" :"lb-3k06q7t0"}'
    req.from_json_string(params)

    resp = clbClient.DescribeTargets(req)
    print(resp.to_json_string())

def DescribeDBInstances():
    req = models.DescribeDBInstancesRequest()
    params = '{}'
    req.from_json_string(params)

    resp = cdbClient.DescribeDBInstances(req)
    print(resp.to_json_string())

def DescribeDCDBInstances():
    req = models.DescribeDCDBInstancesRequest()
    params = '{}'
    req.from_json_string(params)

    resp = dcdbClient.DescribeDCDBInstances(req)
    print(resp.to_json_string())

def list_buckets():
    resp = cosClient.list_buckets()
    resp_ = []
    for i in resp['Buckets']['Bucket']:
        if i['Location'] == regionUU:
            resp_.append(i)
    resp['Buckets']['Bucket'] = resp_
    print("list_buckets", resp)
    for obj in resp['Buckets']['Bucket']:
        print('obj', obj)
        while True:
            response = cosClient.list_objects(
                Bucket=obj['Name']
            )
            print('response',response)
            print('response```',response['Contents'])
            response2 = cosClient.get_bucket_acl(
                Bucket=obj['Name']
            )
            print('response2', response2)
            if response['IsTruncated'] == 'false':
                break
            print('response', response)


def DescribeBaseMetrics():
    req = models.DescribeBaseMetricsRequest()
    params = '{\"Namespace\":\"maguohao\",\"MetricName\":\"cvm\"}'
    req.from_json_string(params)

    resp = monitorClient.DescribeBaseMetrics(req)
    print(resp.to_json_string())

if __name__ == '__main__':
    logging.info("Hello Tencent OpenApi!")
    # DescribeZonesRequest()
    # DescribeInstances()
    # DescribeImages()
    # DescribeDisks()
    # DescribeVpcsResponse()
    # DescribeAddresses()
    # DescribeSecurityGroups()
    # DescribeLoadBalancers()
    # DescribeDBInstances()
    # DescribeDCDBInstances()
    # list_buckets()
    # DescribeBaseMetrics()
    DescribeTargetsResponse()