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
         - name: huawei-global-grants
           resource: huawei.obs
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
        # READ
        #
        # 若有桶的读权限，则可以获取该桶内对象列表、桶内多段任务、桶的元数据、桶的多版本。
        #
        # 若有对象的读权限，则可以获取该对象内容和元数据。
        #
        # WRITE
        #
        # 若有桶的写权限，则可以上传、覆盖和删除该桶内任何对象和段。
        #
        # 此权限在对象上不适用。
        #
        # READ_ACP
        #
        # 若有读ACP的权限，则可以获取对应的桶或对象的权限控制列表（ACL）。
        #
        # 桶或对象的所有者永远拥有读对应桶或对象ACP的权限。
        #
        # WRITE_ACP
        #
        # 若有写ACP的权限，则可以更新对应桶或对象的权限控制列表（ACL）。
        #
        # 桶或对象的所有者永远拥有写对应桶或对象的ACP的权限。
        #
        # 拥有了写ACP的权限，由于可以更改权限控制策略，实际上意味着拥有了完全访问的权限。
        #
        # FULL_CONTROL
        #
        # 若有桶的完全控制权限意味着拥有READ、WRITE、READ_ACP和WRITE_ACP的权限。
        #
        # 若有对象的完全控制权限意味着拥有READ、READ_ACP和WRITE_ACP的权限。
        acl = Session.client(self, service).getBucketAcl(b.name)
        b['permission'] = acl.body.grants
        if 'READ' not in str(acl.body.grants) and 'WRITE' not in str(acl.body.grants):
            return b
        else:
            return

@Obs.action_registry.register('createBucket')
class ObsCreateBucket(MethodAction):

    schema = type_schema('createBucket')
    method_spec = {'op': 'createBucket'}

    def get_request(self, bucket):
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

    def get_request(self, bucket):
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

    def get_request(self, bucket):
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

    def get_request(self, bucket):
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