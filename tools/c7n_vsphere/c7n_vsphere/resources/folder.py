# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n_vsphere.query import QueryResourceManager, TypeInfo
from c7n_vsphere.provider import resources
from c7n_vsphere.client import Session

@resources.register('folder')
class Folder(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'folder'
        name = 'name'
        default_report_fields = ['folder', 'name']

    def get_request(self):
        client = Session.client(self)
        folders = client.vcenter.Folder.list()
        #Summary(folder='group-d1', name='Datacenters', type=Type(string='DATACENTER'))
        res = []
        for item in folders:
            data= {
                "F2CId": item.folder,
                "folder": item.folder,
                "name": item.name,
                "type": str(item.type),
            }
            res.append(data)
        return json.dumps(res)