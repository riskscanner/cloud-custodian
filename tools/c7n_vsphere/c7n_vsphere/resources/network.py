# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('network')
class Network(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'network'
        name = 'name'
        default_report_fields = ['network', 'name']

    def get_request(self):
        client = Session.client(self)
        networks = client.vcenter.Network.list()
        #Summary(network='dvportgroup-1312', name='cluster-try-VSAN-DPortGroup', type=Type(string='DISTRIBUTED_PORTGROUP'))
        res = []
        for item in networks:
            data= {
                "F2CId": item.network,
                "network": item.network,
                "name": item.name,
                "type": str(item.type),
            }
            res.append(data)
        return json.dumps(res)

@Network.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters Networks based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-network-system
                resource: vsphere.network
                filters:
                  - not:
                    - type: system
                      value: DISTRIBUTED_PORTGROUP
    """
    schema = type_schema(
        'system',
        value={'type': 'string'},
    )

    def process(self, resources, event=None):
        results = []
        value = self.data.get('value', None)
        for network in resources:
            matched = True
            if value is not None and value != network.get('type'):
                matched = False
            if matched:
                results.append(network)
        return results