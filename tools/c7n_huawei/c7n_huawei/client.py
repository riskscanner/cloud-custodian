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

from openstack import connection
from obs import ObsClient

log = logging.getLogger('c7n_huawei.client')


class Session:
    """Base class for API repository for a specified Cloud API."""
    # create connection
    # username = os.getenv('HUAWEI_USERNAME')  # 用户名称
    # password = os.getenv('HUAWEI_PASSWORD')  # 用户密码
    # projectId = os.getenv('HUAWEI_PROJECTID')  # 项目ID
    # userDomainId = os.getenv('HUAWEI_USERDOMAINID')  # 账户ID
    # auth_url = "https://iam.example.com/v3"  # endpoint url
    # cloud = os.getenv('HUAWEI_CLOUD')
    # ak = os.getenv('HUAWEI_AK')
    # sk = os.getenv('HUAWEI_SK')
    # region = os.getenv('HUAWEI_DEFAULT_REGION')
    # project_id = os.getenv('HUAWEI_PROJECT')

    def __init__(self, ak=None, sk=None, regionId=None, projectId=None, cloud=None, server=None):
        if not ak:
            ak = os.getenv('HUAWEI_AK')
        if not sk:
            sk = os.getenv('HUAWEI_SK')
        if not regionId:
            regionId = os.getenv('HUAWEI_DEFAULT_REGION')
        if not projectId:
            projectId = os.getenv('HUAWEI_PROJECT')
        if not cloud:
            cloud = os.getenv('HUAWEI_CLOUD')
        if not server:
            server = os.getenv('HUAWEI_ENDPOINT')
        self.ak = ak
        self.sk = sk
        self.region = regionId
        self.project_id = projectId
        self.cloud = cloud
        self.server = server

    def get_default_region(self):
        if self.region:
            return self.region
        for k in ('HUAWEI_DEFAULT_REGION'):
            if k in os.environ:
                return os.environ[k]
            else:
                return 'cn-north-1'

    def client(self, service):
        if service == 'obs':
            # 创建ObsClient实例
            obsClient = ObsClient(
                access_key_id=os.getenv('HUAWEI_AK'),
                secret_access_key=os.getenv('HUAWEI_SK'),
                server=os.getenv('HUAWEI_ENDPOINT')
            )
            clt = obsClient
        else:
            conn = connection.Connection(
                cloud=os.getenv('HUAWEI_CLOUD'),
                ak=os.getenv('HUAWEI_AK'),
                sk=os.getenv('HUAWEI_SK'),
                region=os.getenv('HUAWEI_DEFAULT_REGION'),
                project_id=os.getenv('HUAWEI_PROJECT')
            )
            if 'compute' in service:
                clt = conn.compute
            elif 'vpcv1' in service:
                clt = conn.vpcv1
            elif 'network' in service:
                clt = conn.network
            elif 'block_store' in service:
                clt = conn.block_store
            elif 'rdsv3' in service:
                clt = conn.rdsv3
            elif 'obs' in service:
                clt = conn.rdsv3
            else:
                clt = conn.compute
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

