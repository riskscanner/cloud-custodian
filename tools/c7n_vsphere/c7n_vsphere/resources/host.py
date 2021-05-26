# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('host')
class Host(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'host'
        name = 'name'
        default_report_fields = ['host', 'name']

    def get_request(self):
        client = Session.client(self)
        hosts = client.vcenter.Host.list()
        #Summary(host='host-10', name='10.1.240.15', connection_state=ConnectionState(string='CONNECTED'), power_state=PowerState(string='POWERED_ON'))
        res = []
        for item in hosts:
            data= {
                "F2CId": item.host,
                "host": item.host,
                "name": item.name,
                "connection_state": str(item.connection_state),
                "power_state": str(item.power_state),
            }
            res.append(data)
        return json.dumps(res)

@Host.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters Hosts based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-host-system
                resource: vsphere.host
                filters:
                  - not:
                    - type: system
                      connection_state: CONNECTED
                      power_state: POWERED_ON
    """
    schema = type_schema(
        'system',
        connection_state={'type': 'string'},
        power_state={'type': 'string'},
    )

    def process(self, resources, event=None):
        results = []
        connection_state = self.data.get('connection_state', None)
        power_state = self.data.get('power_state', None)
        for host in resources:
            matched = True
            if connection_state is not None and connection_state != host.get('connection_state'):
                matched = False
            if power_state is not None and power_state != host.get('power_state'):
                matched = False
            if matched:
                results.append(host)
        return results