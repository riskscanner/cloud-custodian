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

from c7n.utils import type_schema
from c7n_huawei.actions import MethodAction
from c7n_huawei.client import Session
from c7n_huawei.provider import resources
from c7n_huawei.query import QueryResourceManager, TypeInfo
from c7n_huawei.filters.filter import HuaweiDiskFilter

service = 'block_store.disk'

@resources.register('disk')
class Disk(QueryResourceManager):

    class resource_type(TypeInfo):
        service = 'block_store.disk'
        enum_spec = (None, None, None)
        id = 'id'

    def get_request(self):
        try:
            volumes = Session.client(self, service).volumes(details=True)
            arr = list()  # 创建 []
            if volumes is not None:
                for volume in volumes:
                    json = dict()  # 创建 {}
                    for name in dir(volume):
                        if not name.startswith('_'):
                            value = getattr(volume, name)
                            if not callable(value):
                                json[name] = value
                    arr.append(json)
        except Exception as err:
            pass
        return arr


@Disk.filter_registry.register('unused')
class HuaweiDiskFilter(HuaweiDiskFilter):
    """Filters:Example:
       .. code-block:: yaml

           policies:
             - name: huawei-disk
               resource: huawei.disk
               filters:
                 - type: unused

    """
    # creating:云硬盘处于正在创建的过程中。
    # available:云硬盘创建成功，还未挂载给任何云服务器，可以进行挂载。
    # in -use:云硬盘已挂载给云服务器，正在使用中。
    # error:云硬盘在创建过程中出现错误。
    # attaching:云硬盘处于正在挂载的过程中。
    # detaching:云硬盘处于正在卸载的过程中。
    # restoring - backup:云硬盘处于正在从备份恢复的过程中。
    # backing - up: 云硬盘处于通过备份创建的过程中。
    # error_restoring:云硬盘从备份恢复过程中出现错误。
    # uploading:云硬盘数据正在被上传到镜像中。此状态出现在从云服务器创建镜像的操作过程中。
    # downloading:正在从镜像下载数据到云硬盘。此状态出现在创建云服务器的操作过程中。
    # extending:云硬盘处于正在扩容的过程中。
    # error_extending:云硬盘在扩容过程中出现错误。
    # deleting:云硬盘处于正在删除的过程中。
    # error_deleting:云硬盘在删除过程中出现错误。
    # rollbacking:云硬盘处于正在从快照回滚数据的过程中。
    schema = type_schema('available')

@Disk.action_registry.register('delete')
class DiskDelete(MethodAction):
    """
         policies:
           - name: huawei-disk-delete
             resource: huawei.disk
             actions:
               - delete
     """
    schema = type_schema('delete')
    method_spec = {'op': 'delete'}
    attr_filter = ('status', ('available','error', None, ))

    def get_request(self, disk):
        Session.client(self, service).delete_volume(disk['id'])