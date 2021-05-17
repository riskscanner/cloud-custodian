# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from c7n.resources import load_resources
from c7n_openstack.client import Session

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/openstack.txt")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "openstack.OS_USERNAME" in line:
            OS_USERNAME = line[line.rfind('=') + 1:]
            json['OS_USERNAME'] = OS_USERNAME
        if "openstack.OS_PASSWORD" in line:
            OS_PASSWORD = line[line.rfind('=') + 1:]
            json['OS_PASSWORD'] = OS_PASSWORD
        if "openstack.OS_REGION_NAME" in line:
            OS_REGION_NAME = line[line.rfind('=') + 1:]
            json['OS_REGION_NAME'] = OS_REGION_NAME
        if "openstack.OS_AUTH_URL" in line:
            OS_AUTH_URL = line[line.rfind('=') + 1:]
            json['OS_AUTH_URL'] = OS_AUTH_URL
        if "openstack.OS_PROJECT_NAME" in line:
            OS_PROJECT_NAME = line[line.rfind('=') + 1:]
            json['OS_PROJECT_NAME'] = OS_PROJECT_NAME
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()
load_resources()

OPENSTACK_CONFIG = {
    'OS_USERNAME': params['OS_USERNAME'],
    'OS_PASSWORD': params['OS_PASSWORD'],
    'OS_REGION_NAME': params['OS_REGION_NAME'],
    'OS_AUTH_URL': params['OS_AUTH_URL'], #http://keystone:5000/v3
    'OS_PROJECT_NAME': params['OS_PROJECT_NAME'],
    'OS_USER_DOMAIN_NAME': 'Default',
    'OS_PROJECT_DOMAIN_NAME': 'Default',
    'OS_IDENTITY_API_VERSION': '3',
    'OS_CLOUD_NAME': 'c7n-cloud',
}

DEFAULT_CASSETTE_FILE = "default.yaml"

def init_openstack_config():
    for k, v in OPENSTACK_CONFIG.items():
        os.environ[k] = v

def list_users(self):
    print("List Users:")
    for user in Session.client(self).list_users(self):
        print(user)

if __name__ == '__main__':
    logging.info("Hello OpenStack OpenApi!")
    list_users(None)