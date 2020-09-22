# Custodian Huawei Support

Status - Alpha

# Features

 - Serverless ✅
 - Api Subscriber ✅
 - Metrics ✅
 - Resource Query ✅
 - Multi Account (c7n-org) ✅

# Getting Started


## via pip

```
pip install -e tools/c7n_huawei
```
```
# 弹性云服务ECS
HUAWEI_USER_DOMAIN=xxxxx
HUAWEI_USERNAME=xxxxx
HUAWEI_PASSWORD=xxxxx
HUAWEI_PROJECT=xxxxx
HUAWEI_DEFAULT_REGION=xxxxx
custodian run -s . policy.yml
```
```
# 对象存储服务OBS
HUAWEI_AK=xxxxx
HUAWEI_SK=xxxxx
HUAWEI_DEFAULT_REGION=cn-southwest-2
HUAWEI_ENDPOINT=xxxx
custodian run -s . policy.yml
```


# Serverless

Custodian supports both periodic and api call events for serverless policy execution.
