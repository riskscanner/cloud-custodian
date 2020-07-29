import logging
import time

from openstack import connection

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/huawei.txt")
    lines = f.readlines()
    for line in lines:
        if "huawei.ak" in line:
            ak = line[line.rfind('=') + 1:line.rfind('|')]
            json['ak'] = ak
        if "huawei.sk" in line:
            sk = line[line.rfind('=') + 1:line.rfind('|')]
            json['sk'] = sk
        if "huawei.cloud" in line:
            cloud = line[line.rfind('=') + 1:line.rfind('|')]
            json['cloud'] = cloud
        if "huawei.region" in line:
            region = line[line.rfind('=') + 1:line.rfind('|')]
            json['region'] = region
        if "huawei.project_id" in line:
            project_id = line[line.rfind('=') + 1:line.rfind('|')]
            json['project_id'] = project_id
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()

conn = connection.Connection(
    project_id=params['project_id'],
    region=params['region'],
    cloud=params['cloud'],
    ak = params['ak'],
    sk = params['sk']
)

def availability_zones():
    azs = conn.compute.availability_zones()
    for az in azs:
        print(az)


# get list of server
def list_servers():
    servers = conn.compute.servers(limit=10000)
    arr = list()  # 创建 []
    for server in servers:
        json = dict()  # 创建 {}
        json = _print_(json, server)
        arr.append(json)
    print(arr)

# find server_id or name
def find_server(server_id):
    json = dict()  # 创建 {}
    server = conn.compute.find_server(server_id)
    json = _print_(json, server)
    print(json)


# show server detail
def show_server(server_id):
    json = dict()  # 创建 {}
    server = conn.compute.get_server(server_id)
    json = _print_(json, server)
    print(json)

# stop server
def stop_server(server_id):
    json = dict()  # 创建 {}
    conn.compute.stop_server(server_id)
    time.sleep(5)
    server = conn.compute.find_server(server_id)
    json = _print_(json, server)
    print(json)

# start server
def start_server(server_id):
    json = dict()  # 创建 {}
    conn.compute.start_server(server_id)
    time.sleep(5)
    server = conn.compute.find_server(server_id)
    json = _print_(json, server)
    print(json)

def ips():
    query = {
        "limit": 10000
    }
    fips = conn.network.ips(**query)
    arr = list()  # 创建 []
    for fip in fips:
        json = dict()  # 创建 {}
        json = _print_(json, fip)
        arr.append(json)
    print(arr)


def find_available_ip():
    fips = conn.network.find_available_ip()
    arr = list()  # 创建 []
    if fips is not None:
        for fip in fips:
            json = dict()  # 创建 {}
            json = _print_(json, fip)
            arr.append(json)
    print(arr)

def vpcs():
    query = {
        "limit": 10000
    }
    vpcs = conn.vpcv1.vpcs(**query)
    arr = list()  # 创建 []
    for vpc in vpcs:
        json = dict()  # 创建 {}
        json = _print_(json, vpc)
        arr.append(json)
    print(arr)

def delete_vpc():
    conn.vpcv1.delete_vpc('1069dd2e-db67-4d0a-bd2f-0205af7e6d63')

def security_groups():
    query = {
        "limit": 10000
    }
    sgs = conn.network.security_groups(**query)
    arr = list()  # 创建 []
    for sg in sgs:
        json = dict()  # 创建 {}
        json = _print_(json, sg)
        arr.append(json)
    print(arr)

def find_security_group(id):
    sg = conn.network.find_security_group(id)
    json = dict()  # 创建 {}
    json = _print_(json, sg)
    print(json)

def rds_instances():
    query = {
        'offset': 0,
        'limit': 100
    }
    rds = conn.rdsv3.instances(**query)
    arr = list()  # 创建 []
    for sg in rds:
        json = dict()  # 创建 {}
        json = _print_(json, sg)
        arr.append(json)
    print(arr)

def _print_(json, item):
    for name in dir(item):
        if not name.startswith('_'):
            value = getattr(item, name)
            if not callable(value):
                json[name] = value
    return json


if __name__ == '__main__':
    logging.info("Hello Huawei OpenApi!")
    # availability_zones()
    # list_servers()
    # find_server('73a55347-ad06-4662-bd06-cc83c7683d2a')
    # show_server('73a55347-ad06-4662-bd06-cc83c7683d2a')
    # stop_server('73a55347-ad06-4662-bd06-cc83c7683d2a')
    # start_server('73a55347-ad06-4662-bd06-cc83c7683d2a')
    # security_groups()
    # ips()
    # find_available_ip()
    # vpcs()
    # find_security_group('xxxx')
    rds_instances()