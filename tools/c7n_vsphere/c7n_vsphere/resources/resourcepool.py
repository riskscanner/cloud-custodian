# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('resourcepool')
class ResourcePool(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'resource_pool'
        name = 'name'
        default_report_fields = ['resource_pool', 'name']

    def get_request(self):
        client = Session.client(self)
        resource_pools = client.vcenter.ResourcePool.list()
        #Summary(resource_pool='resgroup-34', name='Resources')
        res = []
        for item in resource_pools:
            #{name : Resources, resource_pools : set(), cpu_allocation : None, memory_allocation : None}
            resource_pool = client.vcenter.ResourcePool.get(item.resource_pool)
            data= {
                "F2CId": item.resource_pool,
                "resource_pool": item.resource_pool,
                "name": item.name,
                "cpu_allocation": resource_pool.cpu_allocation,
                "memory_allocation": resource_pool.memory_allocation
            }
            res.append(data)
        return json.dumps(res)

@ResourcePool.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters ResourcePools based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-resourcepool-system
                resource: vsphere.resourcepool
                filters:
                  - not:
                    - type: system
                      cpu_allocation: 0
                      memory_allocation: 0
    """
    schema = type_schema(
        'system',
        cpu_allocation={'type': 'number'},
        memory_allocation={'type': 'number'},
    )

    def process(self, resources, event=None):
        results = []
        cpu_allocation = self.data.get('cpu_allocation', None)
        memory_allocation = self.data.get('memory_allocation', None)
        for resourcepool in resources:
            matched = True
            if cpu_allocation is not None and cpu_allocation != resourcepool.get('cpu_allocation'):
                matched = False
            if memory_allocation is not None and memory_allocation != resourcepool.get('memory_allocation'):
                matched = False
            if matched:
                results.append(resourcepool)
        return results