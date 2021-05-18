# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo


@resources.register('volume')
class Volume(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_volumes', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name', 'status', 'size']

@Volume.filter_registry.register('status')
class StatusFilter(Filter):
    """Filters Volumes based on their status
    :example:
    .. code-block:: yaml
            policies:
              - name: openstack-volume
                resource: openstack.volume
                filters:
                  - type: status
                    volume_status: 'in-use'
                    system_scope: true
    """
    schema = type_schema(
        'status',
        is_encrypted={'type': 'boolean'},
        volume_status={'type': 'string'},
        system_scope={'type': 'boolean'},
    )

    def _match_(self, volume, is_encrypted, volume_status, system_scope):
        if is_encrypted:
            if is_encrypted != volume.is_encrypted:
                return True
        if volume_status:
            if volume_status != volume.status:
                return True
        if system_scope:
            if len(volume.attachments) == 0:
                return True
        else:
            if len(volume.attachments) > 0:
                return True
        return False

    def process(self, resources, event=None):
        results = []
        is_encrypted = self.data.get('is_encrypted', None)
        volume_status = self.data.get('volume_status', None)
        system_scope = self.data.get('system_scope', None)
        for volume in resources:
            if self._match_(volume, is_encrypted, volume_status, system_scope):
                results.append(volume)
        return results
