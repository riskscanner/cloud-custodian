# Copyright 2017 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import os

from tencentcloud.common import credential
# 导入可选配置类
# 导入对应产品模块的 client models。
from tencentcloud.cvm.v20170312 import cvm_client
from tencentcloud.cbs.v20170312 import cbs_client
from tencentcloud.vpc.v20170312 import vpc_client
from tencentcloud.clb.v20180317 import clb_client
from tencentcloud.cdb.v20170320 import cdb_client
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

log = logging.getLogger('c7n_tencent.client')


class Session:

    def __init__(self, secretId=None, secretKey=None, regionId=None):
        if not secretId:
            secretId = os.getenv('TENCENT_SECRETID')
        if not secretKey:
            secretKey = os.getenv('TENCENT_SECRETKEY')
        if not regionId:
            regionId = os.getenv('TENCENT_DEFAULT_REGION')
        self.secretId = secretId
        self.secretKey = secretKey
        self.region = regionId

    def get_default_region(self):
        if self.region:
            return self.region
        for k in ('TENCENT_DEFAULT_REGION'):
            if k in os.environ:
                return os.environ[k]
            else:
                return 'ap-shanghai'

    def client(self, service):
        # 实例化一个认证对象，入参需要传入腾讯云账户 secretId，secretKey
        cred = credential.Credential(os.getenv('TENCENT_SECRETID'), os.getenv('TENCENT_SECRETKEY'))

        if 'cvm_client' in service:
            # 实例化要请求产品 (以 cvm 为例) 的 client 对象
            client = cvm_client.CvmClient(cred, os.getenv('TENCENT_DEFAULT_REGION'))
        elif 'cbs_client' in service:
            client = cbs_client.CbsClient(cred, os.getenv('TENCENT_DEFAULT_REGION'))
        elif 'vpc_client' in service:
            client = vpc_client.VpcClient(cred, os.getenv('TENCENT_DEFAULT_REGION'))
        elif 'clb_client' in service:
            client = clb_client.ClbClient(cred, os.getenv('TENCENT_DEFAULT_REGION'))
        elif 'cdb_client' in service:
            client = cdb_client.CdbClient(cred, os.getenv('TENCENT_DEFAULT_REGION'))
        elif 'coss3_client' in service:
            # 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
            config = CosConfig(Region=os.getenv('TENCENT_DEFAULT_REGION'), SecretId=os.getenv('TENCENT_SECRETID'),
                               SecretKey=os.getenv('TENCENT_SECRETKEY'),Endpoint=os.getenv('TENCENT_ENDPOINT'))
            # 2. 获取客户端对象
            client = CosS3Client(config)
        return client

