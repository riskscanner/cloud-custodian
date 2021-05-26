# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('datacenter')
class Datacenter(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'datacenter'
        name = 'name'
        default_report_fields = ['datacenter', 'name']

    def get_request(self):
        client = Session.client(self)
        datacenters = client.vcenter.Datacenter.list()
        #Summary(datacenter='datacenter-2', name='Datacenter')
        res = []
        for item in datacenters:
            #{name : Datacenter, datastore_folder : group-s5, host_folder : group-h4, network_folder : group-n6, vm_folder : group-v3}
            datacenter = client.vcenter.Datacenter.get(item.datacenter)
            data= {
                "F2CId": item.datacenter,
                "datacenter": item.datacenter,
                "name": item.name,
                "datastore_folder": datacenter.datastore_folder,
                "host_folder": datacenter.host_folder,
                "network_folder": datacenter.network_folder,
                "vm_folder": datacenter.vm_folder,
            }
            res.append(data)
        return json.dumps(res)

@Datacenter.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters Datacenters based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-datacenter-system
                resource: vsphere.datacenter
                filters:
                  - not:
                    - type: system
                      host_folder: ''
                      network_folder: ''
                      vm_folder: ''
    """
    schema = type_schema(
        'system',
        host_folder={'type': 'string'},
        network_folder={'type': 'string'},
        vm_folder={'type': 'string'},
    )

    def process(self, resources, event=None):
        results = []
        host_folder = self.data.get('host_folder', None)
        network_folder = self.data.get('network_folder', None)
        vm_folder = self.data.get('vm_folder', None)
        for datacenter in resources:
            matched = True
            if host_folder == datacenter.get('host_folder'):
                matched = False
            if network_folder == datacenter.get('network_folder'):
                matched = False
            if vm_folder == datacenter.get('vm_folder'):
                matched = False
            if matched:
                results.append(datacenter)
        return results