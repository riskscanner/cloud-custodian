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

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkecs.v2 import *
from huaweicloudsdkeip.v2 import *
from huaweicloudsdkelb.v2 import *
from huaweicloudsdkevs.v2 import *
from huaweicloudsdkrds.v3 import *
from huaweicloudsdkrds.v3.region.rds_region import RdsRegion
from huaweicloudsdkvpc.v2 import *
from huaweicloudsdkvpc.v2.region.vpc_region import VpcRegion
from huaweicloudsdkces.v1 import *
from huaweicloudsdkces.v1.region.ces_region import CesRegion
from huaweicloudsdkiam.v3 import *
from huaweicloudsdkiam.v3.region.iam_region import IamRegion
from huaweicloudsdkdcs.v2 import *
from huaweicloudsdkdcs.v2.region.dcs_region import DcsRegion
from huaweicloudsdkdds.v3 import *
from huaweicloudsdkdds.v3.region.dds_region import DdsRegion
from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from obs import ObsClient

log = logging.getLogger('c7n_huawei.client')


class Session:
    """Base class for API repository for a specified Cloud API."""
    # create connection
    # username = os.getenv('HUAWEI_USERNAME')  # 用户名称
    # password = os.getenv('HUAWEI_PASSWORD')  # 用户密码
    # projectId = os.getenv('HUAWEI_PROJECTID')  # 项目ID
    # userDomainId = os.getenv('HUAWEI_USERDOMAINID')  # 账户ID
    # auth_url = 'https://iam.myhuaweicloud.com/v3'  # endpoint url
    # cloud = 'myhuaweicloud.com'
    # ak = os.getenv('HUAWEI_AK')
    # sk = os.getenv('HUAWEI_SK')
    # region = os.getenv('HUAWEI_DEFAULT_REGION')
    # project_id = os.getenv('HUAWEI_PROJECT')

    def __init__(self, ak=None, sk=None, regionId=None, projectId=None):
        if not ak:
            ak = os.getenv('HUAWEI_AK')
        if not sk:
            sk = os.getenv('HUAWEI_SK')
        if not regionId:
            regionId = os.getenv('HUAWEI_DEFAULT_REGION')
        if not projectId:
            projectId = os.getenv('HUAWEI_PROJECT')
        self.ak = ak
        self.sk = sk
        self.region = regionId
        self.project_id = projectId

    def get_default_region(self):
        if os.getenv('HUAWEI_DEFAULT_REGION'):
            return os.getenv('HUAWEI_DEFAULT_REGION')
        else:
            return self.region

    def client(self, service):
        config = HttpConfig.get_default_config()
        config.ignore_ssl_verification = True
        config.timeout = 3
        credentials = BasicCredentials(os.getenv('HUAWEI_AK'), os.getenv('HUAWEI_SK'), os.getenv('HUAWEI_PROJECT'))
        if service == 'obs':
            # 创建ObsClient实例
            clt = ObsClient(
                access_key_id=os.getenv('HUAWEI_AK'),
                secret_access_key=os.getenv('HUAWEI_SK'),
                server='obs.' + os.getenv('HUAWEI_DEFAULT_REGION') + '.myhuaweicloud.com'
            )
        elif service == 'ecs':
            clt = EcsClient.new_builder(EcsClient) \
                .with_http_config(config) \
                .with_credentials(credentials) \
                .with_endpoint("https://ecs." + os.getenv('HUAWEI_DEFAULT_REGION') + ".myhuaweicloud.com") \
                .build()
        elif service == 'disk':
            clt = EvsClient.new_builder(EvsClient) \
                .with_http_config(config) \
                .with_credentials(credentials) \
                .with_endpoint("https://evs." + os.getenv('HUAWEI_DEFAULT_REGION') + ".myhuaweicloud.com") \
                .build()
        elif service == 'eip':
            clt = EipClient.new_builder(EipClient) \
                .with_http_config(config) \
                .with_credentials(credentials) \
                .with_endpoint("https://vpc." + os.getenv('HUAWEI_DEFAULT_REGION') + ".myhuaweicloud.com") \
                .build()
        elif service == 'elb':
            clt = ElbClient.new_builder(ElbClient) \
                .with_http_config(config) \
                .with_credentials(credentials) \
                .with_endpoint("https://elb." + os.getenv('HUAWEI_DEFAULT_REGION') + ".myhuaweicloud.com") \
                .build()
        elif service == 'vpc':
            clt = VpcClient.new_builder(VpcClient) \
                .with_http_config(config) \
                .with_credentials(credentials) \
                .with_endpoint("https://vpc." + os.getenv('HUAWEI_DEFAULT_REGION') + ".myhuaweicloud.com") \
                .build()
        elif service == 'security-group':
            clt = VpcClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(VpcRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        elif service == 'rds':
            clt = RdsClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(RdsRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        elif service == 'ces':
            clt = CesClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(CesRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        elif service == 'iam':
            iam_credentials = GlobalCredentials(os.getenv('HUAWEI_AK'), os.getenv('HUAWEI_SK'))
            clt = IamClient.new_builder() \
                .with_credentials(iam_credentials) \
                .with_region(IamRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        elif service == 'redis':
            clt = DcsClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(DcsRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        elif service == 'dds':
            clt = DdsClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(DdsRegion.value_of(os.getenv('HUAWEI_DEFAULT_REGION'))) \
                .build()
        return clt


REGION_ENDPOINT = {
        'af-south-1': '非洲-约翰内斯堡',
        'cn-north-4': '华北-北京四',
        'cn-north-1': '华北-北京一',
        'cn-east-2': '华东-上海二',
        'cn-east-3': '华东-上海一',
        'cn-south-1': '华南-广州',
        'cn-south-2': '华南-深圳',
        'cn-southwest-2': '西南-贵阳一',
        'ap-southeast-2': '亚太-曼谷',
        'ap-southeast-1': '亚太-香港',
        'ap-southeast-3': '亚太-新加坡'
    }

