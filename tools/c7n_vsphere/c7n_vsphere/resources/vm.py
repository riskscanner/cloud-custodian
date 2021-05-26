# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
#
import json

from c7n.filters import Filter
from c7n.utils import type_schema
from c7n_vsphere.client import Session
from c7n_vsphere.provider import resources
from c7n_vsphere.query import QueryResourceManager, TypeInfo


@resources.register('vm')
class VM(QueryResourceManager):
    class resource_type(TypeInfo):
        enum_spec = ('list', None)
        id = 'vm'
        name = 'name'
        default_report_fields = ['vm', 'name']

    def get_request(self):
        client = Session.client(self)
        vms = client.vcenter.VM.list()
        #Summary(vm='vm-17', name='QA-PROXY', power_state=State(string='POWERED_ON'), cpu_count=2, memory_size_mib=4096)
        #{guest_os : CENTOS_7_64, name : FIT2CLOUD-2.0-TRY2, identity : None, power_state : POWERED_ON, instant_clone_frozen : None, hardware : {version : VMX_14, upgrade_policy : NEVER, upgrade_version : None, upgrade_status : NONE, upgrade_error : None}, boot : {type : BIOS, efi_legacy_boot : None, network_protocol : None, delay : 0, retry : False, retry_delay : 10, enter_setup_mode : False}, boot_devices : [], cpu : {count : 4, cores_per_socket : 1, hot_add_enabled : False, hot_remove_enabled : False}, memory : {size_mib : 16384, hot_add_enabled : False, hot_add_increment_size_mib : None, hot_add_limit_mib : None}, disks : {'2000': Info(label='Hard disk 1', type=HostBusAdapterType(string='SCSI'), ide=None, scsi=ScsiAddressInfo(bus=0, unit=0), sata=None, backing=BackingInfo(type=BackingType(string='VMDK_FILE'), vmdk_file='[Local] FIT2CLOUD-2.0-TRY2/FIT2CLOUD-2.0-TRY2-000001.vmdk'), capacity=107374182400)}, nics : {'4000': Info(label='Network adapter 1', type=EmulationType(string='VMXNET3'), upt_compatibility_enabled=True, mac_type=MacAddressType(string='GENERATED'), mac_address='00:0c:29:24:5d:a3', pci_slot_number=192, wake_on_lan_enabled=False, backing=BackingInfo(type=BackingType(string='STANDARD_PORTGROUP'), network='network-12', network_name='VM Network', host_device=None, distributed_switch_uuid=None, distributed_port=None, connection_cookie=None, opaque_network_type=None, opaque_network_id=None), state=ConnectionState(string='CONNECTED'), start_connected=True, allow_guest_control=True)}, cdroms : {'16000': Info(type=HostBusAdapterType(string='SATA'), label='CD/DVD drive 1', ide=None, sata=SataAddressInfo(bus=0, unit=0), backing=BackingInfo(type=BackingType(string='ISO_FILE'), iso_file='[Local] iso/CentOS-7-x86_64-Minimal-1804.iso', host_device=None, auto_detect=None, device_access_type=None), state=ConnectionState(string='NOT_CONNECTED'), start_connected=True, allow_guest_control=True)}, floppies : {}, parallel_ports : {}, serial_ports : {}, sata_adapters : {'15000': Info(label='SATA controller 0', type=Type(string='AHCI'), bus=0, pci_slot_number=35)}, scsi_adapters : {'1000': Info(label='SCSI controller 0', type=Type(string='PVSCSI'), scsi=ScsiAddressInfo(bus=0, unit=7), pci_slot_number=160, sharing=Sharing(string='NONE'))}}
        res = []
        for item in vms:
            vm = client.vcenter.VM.get(item.vm)
            data= {
                "F2CId": item.vm,
                "vm": item.vm,
                "name": item.name,
                "power_state": str(item.power_state),
                "cpu_count": item.cpu_count,
                "memory_size_mib": item.memory_size_mib,
                "guest_os": str(vm.guest_os),
                "identity": vm.identity,
                "instant_clone_frozen": vm.instant_clone_frozen,
                "hardware": str(vm.hardware),
                "boot": str(vm.boot),
                "boot_devices": vm.boot_devices,
                "cpu": str(vm.cpu),
                "memory": str(vm.memory),
                "disks": str(vm.disks),
            }
            res.append(data)
        return json.dumps(res)

@VM.filter_registry.register('system')
class SystemFilter(Filter):
    """Filters VMs based on their system
    :example:
    .. code-block:: yaml
            policies:
              - name: vsphere-vm-system
                resource: vsphere.vm
                filters:
                  - not:
                    - type: system
                      power_state: POWERED_ON
                      cpu_count: 1
                      memory_size_mib: 1024
    """
    schema = type_schema(
        'system',
        power_state={'type': 'string'},
        cpu_count={'type': 'number'},
        memory_size_mib={'type': 'number'},
    )

    def process(self, resources, event=None):
        results = []
        power_state = self.data.get('power_state', None)
        cpu_count = self.data.get('cpu_count', None)
        memory_size_mib = self.data.get('memory_size_mib', None)
        for vm in resources:
            matched = True
            if power_state is not None and power_state != vm.get('power_state'):
                matched = False
            if cpu_count is not None and cpu_count > vm.get('cpu_count'):
                matched = False
            if memory_size_mib is not None and memory_size_mib > vm.get('memory_size_mib'):
                matched = False
            if matched:
                results.append(vm)
        return results