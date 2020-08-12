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
import logging

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from c7n_tencent.client import Session
from c7n_tencent.provider import resources
from c7n_tencent.query import QueryResourceManager, TypeInfo

service = 'coss3_client.cos'

@resources.register('cos')
class Cos(QueryResourceManager):

    class resource_type(TypeInfo):
        enum_spec = (None, 'Buckets', None)
        id = 'BucketId'

    def get_requst(self):
        try:
            resp = Session.client(self, service).list_buckets()
            # 输出json格式的字符串回包
            # print(resp.to_json_string(indent=2))

            # 也可以取出单个值。
            # 你可以通过官网接口文档或跳转到response对象的定义处查看返回字段的定义。
            # print(resp.to_json_string())
        except TencentCloudSDKException as err:
            import traceback
            # 发生异常，打印异常堆栈
            logging.error(err)
            return traceback.format_exc()
        # tencent 返回的json里居然不是None，而是java的null，活久见
        return resp.to_json_string().replace('null', 'None')