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
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest

from c7n.actions import Action as BaseAction
from c7n.utils import local_session, chunks


class Action(BaseAction):
    pass


class MethodAction(Action):
    """Invoke an api call on each resource.

    Quite a number of procedural actions are simply invoking an api
    call on a filtered set of resources. The exact handling is mostly
    boilerplate at that point following an 80/20 rule. This class is
    an encapsulation of the 80%.
    """

    # method we'll be invoking
    method_spec = ()

    # batch size
    chunk_size = 20

    # implicitly filter resources by state, (attr_name, (valid_enum))
    attr_filter = ()

    # error codes that can be safely ignored
    ignore_error_codes = ()

    permissions = ()
    method_perm = None

    def validate(self):
        if not self.method_spec:
            raise NotImplementedError("subclass must define method_spec")
        return self

    def filter_resources(self, resources):
        rcount = len(resources)
        attr_name, valid_enum = self.attr_filter
        resources = [r for r in resources if r.get(attr_name) in valid_enum]
        if len(resources) != rcount:
            self.log.warning(
                "policy:%s action:%s implicitly filtered %d resources to %d by attr:%s",
                self.manager.ctx.policy.name,
                self.type,
                rcount,
                len(resources),
                attr_name,
            )
        return resources

    def process(self, resources):

        if self.attr_filter:
            resources = self.filter_resources(resources)
        model = self.manager.get_model()
        session = local_session(self.manager.session_factory)
        client = self.get_client(session, model)
        for resource_set in chunks(resources, self.chunk_size):
            self.process_resource_set(client, model, resource_set)

    def process_resource_set(self, client, model, resources):
        result_key = self.method_spec.get('result_key')
        annotation_key = self.method_spec.get('annotation_key')
        for resource in resources:
            requst = self.get_requst(resource)
            result = self.invoke_api(client, requst)
            if result_key and annotation_key:
                resource[annotation_key] = result.get(result_key)

    def invoke_api(self, client, requst):
        try:
            return client.do_action(requst)
        except:
            raise

    def get_permissions(self):
        if self.permissions:
            return self.permissions
        m = self.manager.resource_type
        method = self.method_perm
        if not method and 'op' not in self.method_spec:
            return ()
        if not method:
            method = self.method_spec['op']
        component = m.component
        if '.' in component:
            component = component.split('.')[-1]
        return ("{}.{}.{}".format(
            m.perm_service or m.service, component, method),)

    def get_operation_name(self, model, resource):
        return self.method_spec['op']

    def get_resource_params(self, model, resource):
        raise NotImplementedError("subclass responsibility")

    def get_requst(self, resource):
        raise NotImplementedError("subclass responsibility")

    def get_client(self, session, model):
        return session.client(model.service)
