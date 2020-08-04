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
import os

import oss2
from c7n_aliyun.actions import MethodAction
from c7n_aliyun.client import REGION_ENDPOINT
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo
from c7n.filters import Filter
from c7n.utils import set_annotation

from c7n.utils import type_schema

service = 'oss'
accessKeyId = os.getenv('ALIYUN_ACCESSKEYID')
accessSecret = os.getenv('ALIYUN_ACCESSSECRET')
regionId = os.getenv('ALIYUN_DEFAULT_REGION')
auth = oss2.Auth(accessKeyId, accessSecret)

@resources.register('oss')
class Oss(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'oss'
        enum_spec = (None, 'buckets', None)
        id = 'id'

    def get_requst(self):
        pass

@Oss.filter_registry.register('global-grants')
class GlobalGrantsFilter(Filter):
    """Filters :example:
    .. code-block:: yaml

       policies:
         - name: aliyun-global-grants
           resource: aliyun.oss
           filters:
            - type: global-grants
    """

    schema = type_schema(
        'global-grants',
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
        bucket = oss2.Bucket(auth, b['extranet_endpoint'], b['name'])
        # 有效值：private、public-read、public-read-write
        acl = bucket.get_bucket_acl().acl
        if acl == 'private':
            return

        results = []
        perms = self.data.get('permissions', [])
        if not perms or (perms and acl in perms):
            results.append(acl)

        if results:
            set_annotation(b, 'GlobalPermissions', results)
            return b

@Oss.action_registry.register('create_bucket')
class OssCreateBucket(MethodAction):

    schema = type_schema('create_bucket')
    method_spec = {'op': 'create_bucket'}

    def get_requst(self, bucket):
        try:
            bucket = oss2.Bucket(auth, REGION_ENDPOINT[regionId], bucket['bucketname'])
            bucketConfig = oss2.models.BucketCreateConfig(oss2.BUCKET_STORAGE_CLASS_STANDARD,
                                                          oss2.BUCKET_DATA_REDUNDANCY_TYPE_ZRS)
            resp = bucket.create_bucket(oss2.BUCKET_ACL_PRIVATE, bucketConfig)
            if resp.status < 300:
                # 操作成功
                print('requestId:', resp.requestId)
                # 处理操作成功后业务逻辑
                return resp
            else:
                # 操作失败，获取详细异常信息
                return resp.errorMessage
        except Exception as e:
            import traceback
            # 发生异常，打印异常堆栈
            return traceback.format_exc()

@Oss.action_registry.register('put_object')
class OssPutObject(MethodAction):
    schema = type_schema('put_object')
    method_spec = {'op': 'put_object'}

    def get_requst(self, bucket):
        try:
            headers = dict()
            headers["x-oss-storage-class"] = "Standard"
            headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
            bucket = oss2.Bucket(auth, REGION_ENDPOINT[regionId], bucket['bucketname'])
            resp = bucket.put_object(bucket['objectname'], bucket['obj'], headers)
            if resp.status < 300:
                # 操作成功
                print('requestId:', resp.requestId)
                # 处理操作成功后业务逻辑
                return resp
            else:
                # 操作失败，获取详细异常信息
                return resp.errorMessage
        except Exception as e:
            import traceback
            # 发生异常，打印异常堆栈
            return traceback.format_exc()

@Oss.action_registry.register('get_object_to_file')
class OssGetObject(MethodAction):
    schema = type_schema('get_object_to_file')
    method_spec = {'op': 'get_object_to_file'}

    def get_requst(self, bucket):
        try:
            bucket = oss2.Bucket(auth, REGION_ENDPOINT[regionId], bucket['bucketname'])
            resp = bucket.get_object_to_file(bucket['objectname'], bucket['localFile'])
            if resp.status < 300:
                # 操作成功
                print('requestId:', resp.requestId)
                # 处理操作成功后业务逻辑
                return resp
            else:
                # 操作失败，获取详细异常信息
                return resp.errorMessage
        except Exception as e:
            import traceback
            # 发生异常，打印异常堆栈
            return traceback.format_exc()

@Oss.action_registry.register('delete_object')
class OssDeleteObject(MethodAction):
    schema = type_schema('delete_object')
    method_spec = {'op': 'delete_object'}

    def get_requst(self, bucket):
        try:
            bucket = oss2.Bucket(auth, REGION_ENDPOINT[regionId], bucket['bucketname'])
            resp = bucket.delete_object(bucket['objectname'])
            if resp.status < 300:
                # 操作成功
                print('requestId:', resp.requestId)
                # 处理操作成功后业务逻辑
                return resp
            else:
                # 操作失败，获取详细异常信息
                return resp.errorMessage
        except Exception as e:
            import traceback
            # 发生异常，打印异常堆栈
            return traceback.format_exc()