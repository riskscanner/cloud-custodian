import logging
import os
# -*- coding: utf-8 -*-
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的 client models。
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.cbs.v20170312 import cbs_client, models

# 导入可选配置项
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/tencent.txt")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "tencent.secretId" in line:
            secretId = line[line.rfind('=') + 1:]
            json['secretId'] = secretId
        if "tencent.secretKey" in line:
            secretKey = line[line.rfind('=') + 1:]
            json['secretKey'] = secretKey
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()

# 实例化一个认证对象，入参需要传入腾讯云账户 secretId，secretKey
cred = credential.Credential(params['secretId'], params['secretKey'])

# 实例化要请求产品 (以 cvm 为例) 的 client 对象
client = cvm_client.CvmClient(cred, "ap-shanghai")

CbsClient = cbs_client.CbsClient(cred, "ap-shanghai")

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

if __name__ == '__main__':
    logging.info("Hello Tencent OpenApi!")
    # DescribeZonesRequest()
    # DescribeInstances()
    # DescribeImages()
    DescribeDisks()