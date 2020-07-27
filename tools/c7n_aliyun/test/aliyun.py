import json
import logging

import oss2
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeDisksRequest import DescribeDisksRequest
from aliyunsdkecs.request.v20140526.DescribeEipAddressesRequest import DescribeEipAddressesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeRegionsRequest import DescribeRegionsRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupAttributeRequest import DescribeSecurityGroupAttributeRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupsRequest import DescribeSecurityGroupsRequest
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
# 本地测试用例
def _loadFile_():
    json = dict()
    f = open("/opt/fit2cloud/aliyun.txt")
    lines = f.readlines()
    for line in lines:
        if "aliyun.ak" in line:
            ak = line[line.rfind('=') + 1:line.rfind('|')]
            json['ak'] = ak
        if "aliyun.sk" in line:
            sk = line[line.rfind('=') + 1:line.rfind('|')]
            json['sk'] = sk
        if "aliyun.region" in line:
            region = line[line.rfind('=') + 1:line.rfind('|')]
            json['region'] = region
        if "aliyun.ossAk" in line:
            ossAk = line[line.rfind('=') + 1:line.rfind('|')]
            json['ossAk'] = ossAk
        if "aliyun.ossSk" in line:
            ossSk = line[line.rfind('=') + 1:line.rfind('|')]
            json['ossSk'] = ossSk
    f.close()
    print('认证信息:   ' + str(json))
    return json

params = _loadFile_()

clt = client.AcsClient(params['ak'], params['sk'], params['region'])
auth = oss2.Auth(params['ossAk'], params['ossSk'])

# sample api to list aliyun open api.
def hello_aliyun_regions():
    request = DescribeRegionsRequest()
    response = _send_request(request)
    if response is not None:
        region_list = response.get('Regions').get('Region')
        assert response is not None
        assert region_list is not None
        result = map(_print_region_id, region_list)
        print("region list: %s", result)
        logging.info("region list: %s", result)

# output the instance owned in current region.
def list_instances():
    request = DescribeInstancesRequest()
    response = _send_request(request)
    if response is not None:
        instance_list = response.get('Instances').get('Instance')
        result = map(_print_instance_id, instance_list)
        print("current region include instance %s", result)
        logging.info("current region include instance %s", result)

def delete_ecs(instance_id):
    request = DeleteInstanceRequest()
    request.set_InstanceId(instance_id)
    response = _send_request(request)
    print(response)

def list_disk():
    request = DescribeDisksRequest()
    response = _send_request(request)
    print(response)

def _print_instance_id(item):
    instance_id = item.get('InstanceId');
    return instance_id

def stop_instance(instance_id, force_stop=False):
    request = StopInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_ForceStop(force_stop)
    print("Stop %s command submit successfully.", instance_id)
    logging.info("Stop %s command submit successfully.", instance_id)
    _send_request(request)

def start_instance(instance_id, force_stop=False):
    request = StartInstanceRequest()
    request.set_InstanceId(instance_id)
    print("Stop %s command submit successfully.", instance_id)
    logging.info("Stop %s command submit successfully.", instance_id)
    _send_request(request)


def _print_region_id(item):
    region_id = item.get("RegionId")
    return region_id

# send open api request
def _send_request(request):
    request.set_accept_format('json')
    try:
        response_str = clt.do_action(request)
        logging.info(response_str)
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as e:
        logging.error(e)

def list_vpcs():
    request = DescribeVpcsRequest()
    response = _send_request(request)
    print(response)

def list_sgs_attr():
    request = DescribeSecurityGroupAttributeRequest()
    request.set_SecurityGroupId("sg-wz91ivbj51beax3lbxe9")
    # request.set_SecurityGroupId("sg-wz97n9phkehbdxq06i6r")
    # request.set_SecurityGroupId("sg-wz94u0ntw5fg5xucw2qq")
    # request.set_SecurityGroupId("sg-wz90bcvme2wonpqua34w")
    response = _send_request(request)
    print(response)

def list_sgs():
    request = DescribeSecurityGroupsRequest()
    response = _send_request(request)
    print(response)

def get_metrics():
    request = DescribeMetricListRequest()
    request.set_accept_format('json')
    request.set_StartTime("2020-07-10 10:00:00")
    request.set_Dimensions("{'InstanceId': 'i-wz9dyfzp857jzxcac4mb'}")
    request.set_Period("60")
    request.set_Namespace("acs_ecs_dashboard")
    request.set_MetricName("DiskReadIOPS")
    response = _send_request(request)
    print(response)

def get_oss():
    service = oss2.Service(auth, 'oss-cn-shenzhen.aliyuncs.com')

    list_bucketsResult = service.list_buckets()
    buckets = list_bucketsResult.buckets

    while list_bucketsResult.is_truncated:
        list_bucketsResult = service.list_buckets(marker=list_bucketsResult.next_marker)
        buckets.extend(list_bucketsResult.buckets)
        print(list_bucketsResult.is_truncated)

    for b in buckets:
        print(b.name)

    #
    # print(jmespath.search('buckets',    json.dumps(buckets)))

def get_elb():
    request = DescribeLoadBalancersRequest()
    reponse = _send_request(request)
    print(reponse)


def get_rds():
    request = DescribeDBInstancesRequest()
    reponse = _send_request(request)
    print(reponse)


def get_eip():
    request = DescribeEipAddressesRequest()
    reponse = _send_request(request)
    print(reponse)

if __name__ == '__main__':
    logging.info("Hello Aliyun OpenApi!")
    # list_instances()
    # delete_ecs("i-wz9h7lsnk5beaipnvn97")
    # stop_instance("i-wz9h7lsnk5beaipnvn97")
    # list_instances()
    # get_eip()
    # list_sgs()
