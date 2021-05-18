# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n.utils import type_schema
from c7n_openstack.filters.filter import Filter
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo


@resources.register('router')
class Router(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_routers', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name', 'status', 'ha']

@Router.filter_registry.register('system')
class RouterFilter(Filter):
    """Filters Routers based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: openstack-router
                resource: openstack.router
                filters:
                  - not:
                    - type: system
                      status: ACTIVE
                      ha: true
    """
    schema = type_schema(
        'system',
        status={'type': 'string'},
        ha={'type': 'boolean'},
    )

    def _match_(self, router, status, ha):
        if ha:
            if ha != router.ha:
                return True
        if status:
            if status != router.status:
                return True
        return False

    def process(self, resources, event=None):
        results = []
        status = self.data.get('status', None)
        ha = self.data.get('ha', None)
        for router in resources:
            if self._match_(router, status, ha):
                results.append(router)
        return results
