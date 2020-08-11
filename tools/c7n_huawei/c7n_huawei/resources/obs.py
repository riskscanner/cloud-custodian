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
from c7n.utils import set_annotation
from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo

service = 'obs'

@resources.register('obs')
class Obs(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'obs'
        enum_spec = (None, 'buckets', None)
        id = 'bucketname'

    def get_requst(self):
        try:
            json = list()
            # 列举桶
            resp = Session.client(self, service).listBuckets(isQueryLocation=True)
            if resp.status < 300:
                # 操作成功
                print('requestId:', resp.requestId)
                # 处理操作成功后业务逻辑
                for bucket in resp.body.buckets:
                    # 列举对象
                    json.append(bucket)
                    res = Session.client(self, service).listObjects(bucket.name)
                    for content in res.body.contents:
                        json.append(content)
                return json
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
         - name: huawei-global-grants
           resource: huawei.oss
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
        resp = Session.client(self, service).listBuckets(isQueryLocation=True)
        # 有效值：private、public-read、public-read-write
        acl = resp.get_bucket_acl().acl
        if acl == 'private':
            return

        results = []
        perms = self.data.get('permissions', [])
        if not perms or (perms and acl in perms):
            results.append(acl)

        if results:
            set_annotation(b, 'GlobalPermissions', results)
            return b

@Obs.action_registry.register('createBucket')
class ObsCreateBucket(MethodAction):

    schema = type_schema('createBucket')
    method_spec = {'op': 'createBucket'}

    def get_requst(self, bucket):
        try:
            # 调用createBucket创建桶
            resp = Session.client(self, service).createBucket(bucket['bucketname'])
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
        finally:
            # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
            # ObsClient在调用ObsClient.close方法关闭后不能再次使用
            Session.client(self, service).close()

@Obs.action_registry.register('putContent')
class ObsPutContent(MethodAction):
    schema = type_schema('putContent')
    method_spec = {'op': 'putContent'}

    def get_requst(self, bucket):
        try:
            # 调用putContent接口上传对象到桶内
            # resp = obsClient.putContent('bucketname', 'objectname', 'Hello OBS')
            resp = Session.client(self, service).putContent(bucket['bucketname'], bucket['objectname'], bucket['obj'])
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
        finally:
            # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
            # ObsClient在调用ObsClient.close方法关闭后不能再次使用
            Session.client(self, service).close()

@Obs.action_registry.register('getObject')
class ObsGetObject(MethodAction):
    schema = type_schema('getObject')
    method_spec = {'op': 'getObject'}

    def get_requst(self, bucket):
        try:
            # 调用getObject接口下载桶内对象
            resp = Session.client(self, service).getObject(bucket['bucketname'], bucket['objectname'])
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
        finally:
            # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
            # ObsClient在调用ObsClient.close方法关闭后不能再次使用
            Session.client(self, service).close()

@Obs.action_registry.register('deleteObject')
class ObsDeleteObject(MethodAction):
    schema = type_schema('deleteObject')
    method_spec = {'op': 'deleteObject'}

    def get_requst(self, bucket):
        try:
            # 调用deleteObject接口删除指定桶内的指定对象
            resp = Session.client(self, service).deleteObject(bucket['bucketname'], bucket['objectname'])
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
        finally:
            # 关闭ObsClient，如果是全局ObsClient实例，可以不在每个方法调用完成后关闭
            # ObsClient在调用ObsClient.close方法关闭后不能再次使用
            Session.client(self, service).close()