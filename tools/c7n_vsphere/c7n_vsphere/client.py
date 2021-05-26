# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
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

import requests
from vmware.vapi.vsphere.client import create_vsphere_client

session = requests.session()
session.verify = False
log = logging.getLogger('custodian.vsphere.client')


class Session:
    def __init__(self, regionId=None):
        self.username = os.getenv('VSPHERE_USERNAME')
        self.password = os.getenv('VSPHERE_PASSWORD')
        self.server = os.getenv('VSPHERE_ENDPOINT')
        if not regionId:
            regionId = os.getenv('VSPHERE_DEFAULT_REGION')
        self.regionId = regionId

    def client(self):
        vsphere_client = create_vsphere_client(server=os.getenv('VSPHERE_ENDPOINT'), username=os.getenv('VSPHERE_USERNAME'), password=os.getenv('VSPHERE_PASSWORD'), session=session)
        return vsphere_client