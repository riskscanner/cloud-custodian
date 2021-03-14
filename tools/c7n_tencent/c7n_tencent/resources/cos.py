# Copyright 2017-2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import os

import urllib3
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_tencent.client import Session
from c7n_tencent.filters.filter import TencentFilter
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'coss3_client.cos'
regionId = os.getenv('TENCENT_DEFAULT_REGION')

@resources.register('cos')
class Cos(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'coss3_client.cos'
        enum_spec = (None, 'Buckets.Bucket', None)
        id = 'Name'

    def get_request(self):
        try:
            resp = Session.client(self, service).list_buckets()
            _resp_ = []
            for i in resp['Buckets']['Bucket']:
                if i['Location'] == regionId:
                    _resp_.append(i)
            resp['Buckets']['Bucket'] = _resp_
            for obj in resp['Buckets']['Bucket']:
                if regionId != obj['Location']:
                    continue
                objects = list()
                try:
                    response = Session.client(self, service).list_objects(
                        Bucket=obj['Name']
                    )
                    if response.get("Contents") is None:
                        continue
                    objects.append(response['Contents'])
                    #响应条目是否被截断，布尔值，例如true或false
                    if response['IsTruncated'] == 'false':
                        continue
                    obj['Objects'] = objects
                except Exception as e:  # 捕获requests抛出的如timeout等客户端错误,转化为客户端错误
                    logging.error(str(e))
                    return json.dumps(resp)
        except TencentCloudSDKException as err:
            logging.error(err)
            return json.dumps(resp)
        return json.dumps(resp)



@Cos.filter_registry.register('global-grants')
class GlobalGrantsFilter(Filter):
    """Filters :example:
    .. code-block:: yaml

       policies:
         # 查看您的COS存储桶是否不允许公开读取访问权限。如果某个COS存储桶策略或存储桶 ACL 允许公开读取访问权限，则该存储桶不合规
         - name: tencent-cos-global-grants
           resource: tencent.cos
           filters:
            - type: global-grants
              value: FULL_CONTROL
    """
    schema = type_schema(
        'global-grants',
        **{'value': {'type': 'string'}},
        allow_website={'type': 'boolean'},
        operator={'type': 'string', 'enum': ['or', 'and']},
        permissions={
            'type': 'array', 'items': {
                'type': 'string', 'enum': [
                    'READ', 'WRITE', 'WRITE_ACP', 'READ_ACP', 'FULL_CONTROL']}})

    def process(self, buckets, event=None):
        with self.executor_factory(max_workers=5) as w:
            results = w.map(self.process_bucket, buckets)
            results = list(filter(None, list(results)))
            return results

    def process_bucket(self, b):
        response = Session.client(self, service).get_bucket_acl(
            Bucket=b['Name']
        )
        Grant = response.get('AccessControlList').get('Grant')
        for i in Grant:
            # 指明授予被授权者的存储桶权限，可选值有 FULL_CONTROL，WRITE，READ，分别对应读写权限、写权限、读权限
            if i.get('Permission') == 'FULL_CONTROL':
                b['Permission'] = response
                return b
            else:
                if self.data['value'] in i.get('Permission'):
                    b['Permission'] = response
                    return b
        return False

@Cos.filter_registry.register('bucket-referer')
class BucketRefererCosFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 检测COS Bucket是否开启防盗链开关，已开通视为合规。
            - name: tencent-cos-bucket-referer
              resource: tencent.cos
              filters:
                - type: bucket-referer
                  value: true
    """
    schema = type_schema(
        'bucket-referer',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        result = Session.client(self, service).get_bucket_referer(
            Bucket=i['Name']
        )
        if self.data['value']:
            if result and result.Status == 'Eabled':
                return False
        else:
            if result and result.Status == 'Disabled':
                return False
        i['BucketReferer'] = result
        return i

@Cos.filter_registry.register('encryption')
class BucketEncryptionCosFilter(TencentFilter):
    """Filters
       :Example:
       .. code-block:: yaml

        policies:
            # 查看并确认您的COS存储桶启用了默认加密，未开启则该存储桶不合规
            - name: tencent-cos-encryption
              resource: tencent.cos
              filters:
                - type: encryption
                  value: true
    """
    schema = type_schema(
        'encryption',
        **{'value': {'type': 'boolean'}})

    def get_request(self, i):
        try:
            result = Session.client(self, service).get_bucket_encryption(
                Bucket=i['Name']
            )
            if self.data['value']:
                if 'Error' in result:
                    return i
                else:
                    if result and result.ServerSideEncryptionConfiguration:
                        return False
                return i
            else:
                if 'Error' in result:
                    return False
                else:
                    if result and result.ServerSideEncryptionConfiguration:
                        return i
                return False
        except TencentCloudSDKException as err:
            pass
        return False