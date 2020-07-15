# Copyright 2018 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import partial

from c7n.provider import Provider, clouds
from c7n.registry import PluginRegistry
from c7n.utils import local_session
from .session import Session

from c7n_azure.resources.resource_map import ResourceMap
from msrestazure.azure_cloud import (AZURE_CHINA_CLOUD, AZURE_GERMAN_CLOUD, AZURE_PUBLIC_CLOUD,
                                     AZURE_US_GOV_CLOUD)
import logging
import sys

log = logging.getLogger('custodian.provider')


@clouds.register('azure')
class Azure(Provider):

    display_name = 'Azure'
    resource_prefix = 'azure'
    resources = PluginRegistry('%s.resources' % resource_prefix)
    resource_map = ResourceMap
    region_to_cloud = {
        'AzureCloud': AZURE_PUBLIC_CLOUD,
        'AzureChinaCloud': AZURE_CHINA_CLOUD,
        'AzureGermanyCloud': AZURE_GERMAN_CLOUD,
        'AzureUSGov': AZURE_US_GOV_CLOUD
    }

    cloud = None

    def initialize(self, options):
        self._set_cloud(options)
        if options['account_id'] is None:
            session = local_session(self.get_session_factory(options))
            options['account_id'] = session.get_subscription_id()
        options['cache'] = 'memory'
        return options

    def initialize_policies(self, policy_collection, options):
        return policy_collection

    def get_session_factory(self, options):
        base_url = self.get_cloud_base_url()

        return partial(Session,
                       subscription_id=options.account_id,
                       authorization_file=options.authorization_file,
                       base_url=base_url)

    def _set_cloud(self, options):
        if self.cloud:
            return

        cloud_list = options.get('regions')

        if not cloud_list:
            self.cloud = AZURE_PUBLIC_CLOUD
            return

        # Only support passing in one cloud at a time
        cloud = self.region_to_cloud.get(cloud_list[0])

        if cloud:
            self.cloud = cloud
        else:
            log.error('Region Flag: %s not recognized, please choose an Azure Cloud from'
                      'the following: AzureCloud, AzureChinaCloud, AzureGermanyCloud, AzureUSGov'
                      % cloud_list[0])
            sys.exit(1)

    def get_cloud_base_url(self):
        if self.cloud:
            return self.cloud.endpoints.resource_manager

        return None


resources = Azure.resources