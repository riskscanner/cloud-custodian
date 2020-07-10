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
        clt = client.AcsClient(self.accessKeyId, self.accessSecret, self.regionId)
        # clt.do_action_with_exception()
        return clt

# ALIYUN_ACCESSKEYID='LTAIHlH2EaYXRLNP' ALIYUN_ACCESSSECRET='pr8OIrmhf7xCMtkrQiTkjIJLGIu7YM' ALIYUN_DEFAULT_REGION='cn-shenzhen' custodian run -s . aliyun.yml