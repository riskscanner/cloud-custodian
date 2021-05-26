# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('datastore')
class Datastore(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'datastore'
        name = 'name'
        default_report_fields = ['datastore', 'name']

    def get_request(self):
        client = Session.client(self)
        datastores = client.vcenter.Datastore.list()
        #Summary(datastore='datastore-1013', name='datastore1', type=Type(string='VMFS'), free_space=610890940416, capacity=991600574464)
        res = []
        for item in datastores:
            #{name : datastore1, type : VMFS, accessible : True, free_space : 610536521728, multiple_host_access : False, thin_provisioning_supported : True}
            datastore = client.vcenter.Datastore.get(item.datastore)
            data= {
                "F2CId": item.datastore,
                "datastore": item.datastore,
                "name": item.name,
                "type": str(item.type),
                "free_space": item.free_space,
                "capacity": item.capacity,
                "accessible": datastore.accessible,
                "multiple_host_access": datastore.multiple_host_access,
                "thin_provisioning_supported": datastore.thin_provisioning_supported,
            }
            res.append(data)
        return json.dumps(res)

@Datastore.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters Datastores based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-datastore-system
                resource: vsphere.datastore
                filters:
                  - not:
                    - type: system
                      free_space: 500
                      thin_provisioning_supported: true
                      multiple_host_access: true
    """
    schema = type_schema(
        'system',
        free_space={'type': 'number'},
        thin_provisioning_supported={'type': 'boolean'},
        multiple_host_access={'type': 'boolean'},
    )

    def process(self, resources, event=None):
        results = []
        free_space = self.data.get('free_space', None)
        thin_provisioning_supported = self.data.get('thin_provisioning_supported', None)
        multiple_host_access = self.data.get('multiple_host_access', None)
        for datastore in resources:
            matched = True
            if free_space is not None and free_space*1024*1024*1024 > datastore.get('free_space'):
                matched = False
            if thin_provisioning_supported and thin_provisioning_supported != datastore.get('thin_provisioning_supported'):
                matched = False
            if multiple_host_access and multiple_host_access != datastore.get('multiple_host_access'):
                matched = False
            if matched:
                results.append(datastore)
        return results