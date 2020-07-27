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

import oss2
from aliyunsdkcore import client

log = logging.getLogger('c7n_aliyun.client')


class Session:
    """Base class for API repository for a specified Cloud API."""

    def __init__(self, accessKeyId=None, accessSecret=None, regionId=None):
        if not accessKeyId:
            accessKeyId = os.getenv('ALIYUN_ACCESSKEYID')
        if not accessSecret:
            accessSecret = os.getenv('ALIYUN_ACCESSSECRET')
        if not regionId:
            regionId = os.getenv('ALIYUN_DEFAULT_REGION')

        self.accessKeyId = accessKeyId
        self.accessSecret = accessSecret
        self.regionId = regionId

    def get_default_region(self):
        if self.regionId:
            return self.regionId
        for k in ('ALIYUN_DEFAULT_REGION'):
            if k in os.environ:
                return os.environ[k]


    def client(self,  service):
        if service == 'oss':
            auth = oss2.Auth(self.accessKeyId, self.accessSecret)
            clt = oss2.Service(auth, REGION_ENDPOINT[self.regionId])
        else:
            clt = client.AcsClient(self.accessKeyId, self.accessSecret, self.regionId)
        return clt




REGION_ENDPOINT = {
        'cn-hangzhou': 'oss-cn-hangzhou.aliyuncs.com',
        'cn-shanghai': 'oss-cn-shanghai.aliyuncs.com',
        'cn-qingdao': 'oss-cn-qingdao.aliyuncs.com',
        'cn-beijing': 'oss-cn-beijing.aliyuncs.com',
        'cn-zhangjiakou': 'oss-cn-zhangjiakou.aliyuncs.com',
        'cn-huhehaote': 'oss-cn-huhehaote.aliyuncs.com',
        'cn-shenzhen': 'oss-cn-shenzhen.aliyuncs.com',
        'cn-hongkong': 'oss-cn-hongkong.aliyuncs.com',
        'us-west-1': 'oss-us-west-1.aliyuncs.com',
        'us-east-1': 'oss-us-east-1.aliyuncs.com',
        'ap-southeast-1': 'oss-ap-southeast-1.aliyuncs.com',
        'ap-southeast-2': 'oss-ap-southeast-2.aliyuncs.com',
        'ap-southeast-3': 'oss-ap-southeast-3.aliyuncs.com',
        'ap-southeast-5': 'oss-ap-southeast-5.aliyuncs.com',
        'ap-northeast-1': 'oss-ap-northeast-1.aliyuncs.com',
        'ap-south-1': 'oss-ap-south-1.aliyuncs.com',
        'eu-central-1': 'oss-eu-central-1.aliyuncs.com',
        'eu-west-1': 'oss-eu-west-1.aliyuncs.com',
        'me-east-1': 'oss-me-east-1.aliyuncs.com'
    }