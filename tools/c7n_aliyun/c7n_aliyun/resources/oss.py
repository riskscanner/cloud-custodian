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
from c7n_aliyun.provider import resources
from c7n_aliyun.query import QueryResourceManager, TypeInfo

from c7n.filters import Filter
from c7n.utils import set_annotation
from c7n.utils import type_schema

service = 'oss'
accessKeyId = os.getenv('ALIYUN_ACCESSKEYID')
accessSecret = os.getenv('ALIYUN_ACCESSSECRET')
regionId = os.getenv('ALIYUN_DEFAULT_REGION')

@resources.register('oss')
class Oss(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'oss'
        enum_spec = (None, 'buckets', None)
        id = 'id'

    def get_request(self):
        return regionId

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
        auth = oss2.Auth(accessKeyId, accessSecret)
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