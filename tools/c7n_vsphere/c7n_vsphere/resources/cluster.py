# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('cluster')
class Cluster(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'cluster'
        name = 'name'
        default_report_fields = ['cluster', 'name']

    def get_request(self):
        client = Session.client(self)
        clusters = client.vcenter.Cluster.list()
        #Summary(cluster='domain-c33', name='cluster-try', ha_enabled=False, drs_enabled=False)
        res = []
        for item in clusters:
            cluster = client.vcenter.Cluster.get(item.cluster)
            data= {
                "F2CId": item.cluster,
                "cluster": item.cluster,
                "name": item.name,
                "ha_enabled": item.ha_enabled,
                "drs_enabled": item.drs_enabled,
                "resource_pool": cluster.resource_pool
            }
            res.append(data)
        return json.dumps(res)

@Cluster.filter_registry.register('ha-enabled')
class HaFilter(Filter):
    """Filters Clusters based on their ha_enabled
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-cluster-ha-enabled
                resource: vsphere.cluster
                filters:
                  - not:
                    - type: ha-enabled
                      value: true
    """
    schema = type_schema(
        'ha-enabled',
        value={'type': 'boolean'},
    )

    def process(self, resources, event=None):
        results = []
        value = self.data.get('value', None)
        for cluster in resources:
            matched = True
            if value is not None and value != cluster.get('ha_enabled'):
                matched = False
            if matched:
                results.append(cluster)
        return results

