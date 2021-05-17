# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n.filters import Filter
from c7n.utils import local_session
from c7n.utils import type_schema
from c7n_openstack.provider import resources
from c7n_openstack.query import QueryResourceManager, TypeInfo


@resources.register('image')
class Image(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list_images', None)
        id = 'id'
        name = 'name'
        default_report_fields = ['id', 'name', 'status', 'visibility']

@Image.filter_registry.register('status')
class StatusFilter(Filter):
    """Filters Images based on their status
    :example:
    .. code-block:: yaml
            policies:
              - name: openstack-image
                resource: openstack.image
                filters:
                  - not:
                    - type: status
                      image_name: centos
                      visibility: private
                      status: active
    """
    schema = type_schema(
        'status',
        image_name={'type': 'string'},
        visibility={'type': 'string'},
        status={'type': 'string'}
    )

    def process(self, resources, event=None):
        results = []
        image_name = self.data.get('image_name', None)
        visibility = self.data.get('visibility', None)
        status = self.data.get('status', None)

        for image in resources:
            matched = True
            if not image:
                if status == "absent":
                    results.append(image)
                continue
            if image_name is not None and image_name != image.name:
                matched = False
            if visibility is not None and visibility != image.visibility:
                matched = False
            if status is not None and status != image.status:
                matched = False
            if matched:
                results.append(image)
        return results

