# Copyright 2017-2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "Li
# cense");
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

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_huawei.client import Session
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'obs'

@resources.register('obs')
class Obs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'obs'
        enum_spec = (None, 'body.buckets', None)
        id = 'name'

    def get_request(self):
        try:
            # 列举桶
            resp = Session.client(self, service).listBuckets(isQueryLocation=True)
            if resp.status < 300:
                arrs = list()
                # 操作成功
                # 处理操作成功后业务逻辑
                for bucket in resp.body.buckets:
                    if Session.get_default_region(self) != bucket.location:
                        arrs.append(bucket)
                    else:
                        # 列举对象
                        res = Session.client(self, service).listObjects(bucket.name)
                        if res.status < 300:
                            bucket['contents'] = res.body.contents
                        else:
                            bucket['contents'] = []
                for arr in arrs:
                    resp.body.buckets.remove(arr)
                return resp
            else:
                # 操作失败，获取详细异常信息
                return resp.errorMessage
        except Exception as e:
            import traceback
            # 发生异常，打印异常堆栈
            return traceback.format_exc()
        finally:
            # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
            # ObsClient在调用ObsClient.close方法关闭后不能再次使用
            Session.client(self, service).close()


@Obs.filter_registry.register('global-grants')
class GlobalGrantsFilter(Filter):
    """Filters :example:
    .. code-block:: yaml

       policies:
         # 查看您的OBS存储桶是否不允许公开读取访问权限。如果某个OBS存储桶策略或存储桶 ACL 允许公开读取访问权限，则该存储桶不合规
         - name: huawei-obs-global-grants
           resource: huawei.obs
           filters:
            - type: global-grants
              value: read
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
        # PRIVATE
        #
        # 私有读写。
        #
        # PUBLIC_READ
        #
        # 公共读。
        #
        # PUBLIC_READ_WRITE
        #
        # 公共读写。
        #
        # PUBLIC_READ_DELIVERED
        #
        # 桶公共读，桶内对象公共读。
        #
        # PUBLIC_READ_WRITE_DELIVERED
        #
        # 桶公共读写，桶内对象公共读写。
        #
        # BUCKET_OWNER_FULL_CONTROL
        #
        # 桶或对象所有者拥有完全控制权限。
        acl = Session.client(self, service).getBucketAcl(b.name)
        b['permission'] = acl.body.grants
        if self.data['value'] is None or self.data['value'] == 'read':
            if 'READ' not in str(acl.body.grants) and 'WRITE' not in str(acl.body.grants):
                return b
        if self.data['value'] == 'write':
            if 'READ' not in str(acl.body.grants) and 'WRITE' not in str(acl.body.grants):
                return b
        return False