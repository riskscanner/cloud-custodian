# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo


@resources.register('flavor')
class Flavor(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_flavors', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name', 'vcpus', 'ram', 'disk']

@Flavor.filter_registry.register('system')
class FlavorFilter(Filter):
    """Filters Flavors based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: openstack-flavor
                resource: openstack.flavor
                filters:
                  - type: system
                    is_public: true
                    ram: 512
                    vcpus: 1
                    disk: 1
    """

    schema = type_schema(
        'system',
        is_public={'type': 'boolean'},
        ram={'type': 'number'},
        vcpus={'type': 'number'},
        disk={'type': 'number'},
    )

    def _match_(self, flavor, is_public, ram, vcpus, disk):
        if is_public:
            if is_public != flavor.is_public:
                return True
        else:
            if is_public == flavor.is_public:
                return True
        if ram:
            if flavor.ram > ram:
                return True
        if vcpus:
            if flavor.vcpus > vcpus:
                return True
        if disk:
            if flavor.disk > disk:
                return True
        return False

    def process(self, resources, event=None):
        results = []
        is_public = self.data.get('is_public', None)
        ram = self.data.get('ram', None)
        vcpus = self.data.get('vcpus', None)
        disk = self.data.get('disk', None)
        for flavor in resources:
            if self._match_(flavor, is_public, ram, vcpus, disk):
                results.append(flavor)
        return results