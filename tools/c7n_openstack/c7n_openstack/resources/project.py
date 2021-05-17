# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
from c7n_openstack.query import QueryResourceManager, TypeInfo
from c7n_openstack.provider import resources
from c7n.utils import local_session
from c7n.utils import type_schema
from c7n.filters import Filter


@resources.register('project')
class Project(QueryResourceManager):
    class resource_type(TypeInfo):
        id = 'id'
        name = 'name'
        enum_spec = ('list_projects', None)
        default_report_fields = ['id', 'name']

@Project.filter_registry.register('user')
class UserFilter(Filter):
    """Filters Projects based on their user
    :example:
    .. code-block:: yaml
            policies:
              - name: demo
                resource: openstack.project
                filters:
                  - type: user
                    system_scope: true
    """
    schema = type_schema(
        'user',
        system_scope={'type': 'boolean'},
    )

    def process(self, resources, event=None):
        results = []
        system_scope = self.data.get('system_scope', None)
        openstack = local_session(self.manager.session_factory).client()
        for project in resources:
            users = openstack.list_users()
            params = []
            for user in users:
                if system_scope:
                    if user.default_project_id != project.id:
                        params.append(user)
                else:
                    if user.default_project_id == project.id:
                        params.append(user)
            if len(params) == 0:
                results.append(project)
        return results