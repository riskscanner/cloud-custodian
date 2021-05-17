# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo
from c7n.filters import Filter
from c7n.utils import type_schema

@resources.register('network')
class Network(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_networks', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name', 'status', 'shared']

@Network.filter_registry.register('system')
class NetworkFilter(Filter):
    """Filters Networks based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: openstack-network
                resource: openstack.network
                filters:
                  - not:
                    - type: system
                      status: ACTIVE
                      shared: false
                      port_security_enabled: true
    """
    schema = type_schema(
        'system',
        status={'type': 'string'},
        shared={'type': 'boolean'},
        port_security_enabled={'type': 'boolean'},
    )

    def _match_(self, network, status, shared, port_security_enabled):
        if status:
            if status != network.status:
                return True
        if shared:
            if shared != network.shared:
                return True
        if port_security_enabled:
            if port_security_enabled != network.port_security_enabled:
                return True
        return False

    def process(self, resources, event=None):
        results = []
        status = self.data.get('status', None)
        shared = self.data.get('shared', None)
        port_security_enabled = self.data.get('port_security_enabled', None)
        for network in resources:
            if self._match_(network, status, shared, port_security_enabled):
                results.append(network)
        return results
