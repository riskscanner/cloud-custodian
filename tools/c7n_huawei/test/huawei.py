import json
import logging

from openstack import connection

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例，不要将key提交到github
conn = connection.Connection(
    # auth_url='https://iam.myhuaweicloud.com/v3',
    # user_domain_id='05825ea8f9000f691fc7c015c9ab1bae',
    # domain_id='05825ea7c40010ea0f44c015ef917ee0',
    # username='wei-fit2cloud',
    # password='Fit2cloud@2020',
    project_id='083e6bd82500f2632fe8c015ba76656b',
    region='cn-southwest-2',
    cloud='myhuaweicloud.com',
    ak = 'UVGHSERXQEJ27VOWPJBO',
    sk = 'zO4VKKEEjbgniiDN8ZQDNMja9ljZU5lB6AIP9BES'
)

def availability_zones():
    azs = conn.compute.availability_zones()
    for az in azs:
        print(az)


# get list of server
def list_servers():
    servers = conn.compute.servers(limit=10000)
    l = list()
    for server in servers:
        d = dict()
        for name in dir(server):
            if not name.startswith('_'):
                value = getattr(server,name)
                if not callable(value):
                    d[name] = value
        l.append(d)
        print(json.dumps(d))

    print(json.dumps(l))
# find server_id or name
def find_server(server_id):
    server = conn.compute.find_server(server_id)
    print(json.loads(server))


# show server detail
def show_server(server_id):
    server = conn.compute.get_server(server_id)
    print(json.loads(server))

def _print_region_id(item):
    region_id = item.get("RegionId")
    return region_id

def _print_instance_id(item):
    instance_id = item.get('InstanceId');
    return instance_id

if __name__ == '__main__':
    logging.info("Hello Huawei OpenApi!")
    # availability_zones()
    list_servers()
    # find_server('97007316-1ac2-40b1-a8a8-8cd60225301d')
    # show_server('97007316-1ac2-40b1-a8a8-8cd60225301d')