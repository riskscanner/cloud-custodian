# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
import logging

import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client

from c7n.resources import load_resources

session = requests.session()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/vsphere.txt")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "vsphere.VSPHERE_USERNAME" in line:
            VSPHERE_USERNAME = line[line.rfind('=') + 1:]
            json['VSPHERE_USERNAME'] = VSPHERE_USERNAME
        if "vsphere.VSPHERE_PASSWORD" in line:
            VSPHERE_PASSWORD = line[line.rfind('=') + 1:]
            json['VSPHERE_PASSWORD'] = VSPHERE_PASSWORD
        if "vsphere.VSPHERE_REGION_NAME" in line:
            VSPHERE_REGION_NAME = line[line.rfind('=') + 1:]
            json['VSPHERE_REGION_NAME'] = VSPHERE_REGION_NAME
        if "vsphere.VSPHERE_SERVER" in line:
            VSPHERE_SERVER = line[line.rfind('=') + 1:]
            json['VSPHERE_SERVER'] = VSPHERE_SERVER
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()
load_resources()

# Disable cert verification for demo purpose.
# This is not recommended in a production environment.
session.verify = False

# Disable the secure connection warning for demo purpose.
# This is not recommended in a production environment.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to a vCenter Server using username and password
vsphere_client = create_vsphere_client(server=params['VSPHERE_SERVER'], username=params['VSPHERE_USERNAME'], password=params['VSPHERE_PASSWORD'], session=session)

def vm_list():
    vms = vsphere_client.vcenter.VM.list()
    res = []
    for item in vms:
        vm = vsphere_client.vcenter.VM.get(item.vm)
        #{guest_os : CENTOS_7_64, name : FIT2CLOUD-2.0-TRY2, identity : None, power_state : POWERED_ON, instant_clone_frozen : None,
        # hardware : {version : VMX_14, upgrade_policy : NEVER, upgrade_version : None, upgrade_status : NONE, upgrade_error : None},
        # boot : {type : BIOS, efi_legacy_boot : None, network_protocol : None, delay : 0, retry : False, retry_delay : 10, enter_setup_mode : False},
        # boot_devices : [], cpu : {count : 4, cores_per_socket : 1, hot_add_enabled : False, hot_remove_enabled : False},
        # memory : {size_mib : 16384, hot_add_enabled : False, hot_add_increment_size_mib : None, hot_add_limit_mib : None},
        # disks : {'2000': Info(label='Hard disk 1', type=HostBusAdapterType(string='SCSI'), ide=None, scsi=ScsiAddressInfo(bus=0, unit=0), sata=None,
        # backing=BackingInfo(type=BackingType(string='VMDK_FILE'), vmdk_file='[Local] FIT2CLOUD-2.0-TRY2/FIT2CLOUD-2.0-TRY2-000001.vmdk'), capacity=107374182400)},
        # nics : {'4000': Info(label='Network adapter 1', type=EmulationType(string='VMXNET3'), upt_compatibility_enabled=True,
        # mac_type=MacAddressType(string='GENERATED'), mac_address='00:0c:29:24:5d:a3', pci_slot_number=192, wake_on_lan_enabled=False,
        # backing=BackingInfo(type=BackingType(string='STANDARD_PORTGROUP'), network='network-12', network_name='VM Network', host_device=None,
        # distributed_switch_uuid=None, distributed_port=None, connection_cookie=None, opaque_network_type=None, opaque_network_id=None),
        # state=ConnectionState(string='CONNECTED'), start_connected=True, allow_guest_control=True)}, cdroms : {'16000': Info(type=HostBusAdapterType(string='SATA'),
        # label='CD/DVD drive 1', ide=None, sata=SataAddressInfo(bus=0, unit=0), backing=BackingInfo(type=BackingType(string='ISO_FILE'),
        # iso_file='[Local] iso/CentOS-7-x86_64-Minimal-1804.iso', host_device=None, auto_detect=None, device_access_type=None),
        # state=ConnectionState(string='NOT_CONNECTED'), start_connected=True, allow_guest_control=True)}, floppies : {}, parallel_ports : {}, serial_ports : {},
        # sata_adapters : {'15000': Info(label='SATA controller 0', type=Type(string='AHCI'), bus=0, pci_slot_number=35)},
        # scsi_adapters : {'1000': Info(label='SCSI controller 0', type=Type(string='PVSCSI'), scsi=ScsiAddressInfo(bus=0, unit=7), pci_slot_number=160,
        # sharing=Sharing(string='NONE'))}}
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
    print(res)
    return res

def cluster_list():
    clusters = vsphere_client.vcenter.Cluster.list()
    res = []
    for item in clusters:
        cluster = vsphere_client.vcenter.Cluster.get(item.cluster)
        data= {
            "F2CId": item.cluster,
            "cluster": item.cluster,
            "name": item.name,
            "ha_enabled": item.ha_enabled,
            "drs_enabled": item.drs_enabled,
            "resource_pool": cluster.resource_pool
        }
        res.append(data)
    print(res)
    return res

def datacenter_list():
    datacenters = vsphere_client.vcenter.Datacenter.list()
    res = []
    for item in datacenters:
        #{name : Datacenter, datastore_folder : group-s5, host_folder : group-h4, network_folder : group-n6, vm_folder : group-v3}
        datacenter = vsphere_client.vcenter.Datacenter.get(item.datacenter)
        print(datacenter)
        data= {
            "F2CId": item.datacenter,
            "datacenter": item.datacenter,
            "name": item.name,
            "datastore_folder": datacenter.datastore_folder,
            "host_folder": datacenter.host_folder,
            "network_folder": datacenter.network_folder,
            "vm_folder": datacenter.vm_folder,
        }
        res.append(data)
    return res

def datastore_list():
    datastores = vsphere_client.vcenter.Datastore.list()
    res = []
    for item in datastores:
        #{name : datastore1, type : VMFS, accessible : True, free_space : 610536521728, multiple_host_access : False, thin_provisioning_supported : True}
        datastore = vsphere_client.vcenter.Datastore.get(item.datastore)
        print(datastore)
        data= {
            "F2CId": item.datastore,
            "datastore": item.datastore,
            "name": item.name,
            "type": str(item.type),
            "free_space": item.free_space,
            "capacity": item.capacity,
            "accessible": datastore.accessible,
            "multiple_host_access": datastore.multiple_host_access,
            "thin_provisioning_supported": datastore.thin_provisioning_supported,
        }
        res.append(data)
    return res

def folder_list():
    folders = vsphere_client.vcenter.Folder.list()
    #Summary(folder='group-d1', name='Datacenters', type=Type(string='DATACENTER'))
    res = []
    for item in folders:
        data= {
            "F2CId": item.folder,
            "folder": item.folder,
            "name": item.name,
            "type": str(item.type),
        }
        res.append(data)
    print(res)
    return folders

def host_list():
    hosts = vsphere_client.vcenter.Host.list()
    #Summary(host='host-10', name='10.1.240.15', connection_state=ConnectionState(string='CONNECTED'), power_state=PowerState(string='POWERED_ON'))
    res = []
    for item in hosts:
        data= {
            "F2CId": item.host,
            "host": item.host,
            "name": item.name,
            "connection_state": str(item.connection_state),
            "power_state": str(item.power_state),
        }
        res.append(data)
    print(res)
    return res

def network_list():
    networks = vsphere_client.vcenter.Network.list()
    #Summary(network='dvportgroup-1312', name='cluster-try-VSAN-DPortGroup', type=Type(string='DISTRIBUTED_PORTGROUP'))
    res = []
    for item in networks:
        data= {
            "F2CId": item.network,
            "network": item.network,
            "name": item.name,
            "type": str(item.type),
        }
        res.append(data)
    print(res)
    return res

def resource_pool_list():
    resource_pools = vsphere_client.vcenter.ResourcePool.list()
    #Summary(resource_pool='resgroup-34', name='Resources')
    res = []
    for item in resource_pools:
        #{name : Resources, resource_pools : set(), cpu_allocation : None, memory_allocation : None}
        resource_pool = vsphere_client.vcenter.ResourcePool.get(item.resource_pool)
        data= {
            "F2CId": item.resource_pool,
            "resource_pool": item.resource_pool,
            "name": item.name,
            "cpu_allocation": resource_pool.cpu_allocation,
            "memory_allocation": resource_pool.memory_allocation
        }
        res.append(data)
    print(res)
    return res

if __name__ == '__main__':
    logging.info("Hello vSphere OpenApi!")
    vm_list()
    # cluster_list()
    # datacenter_list()
    # datastore_list()
    # folder_list()
    # host_list()
    # network_list()
    # resource_pool_list()