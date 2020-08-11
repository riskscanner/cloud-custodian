# Custodian Tencent Support

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
pip install -e tools/c7n_tencent
```
```
# 弹性云服务ECS
TENCENT_AK=xxxxx
TENCENT_SK=xxxxx
TENCENT_DEFAULT_REGION=cn-southwest-2
TENCENT_PROJECT=xxxxx
TENCENT_CLOUD=xxxx
custodian run -s . policy.yml
```
```
# 对象存储服务OBS
TENCENT_AK=xxxxx
TENCENT_SK=xxxxx
TENCENT_DEFAULT_REGION=cn-southwest-2
TENCENT_ENDPOINT=xxxx
custodian run -s . policy.yml
```


# Serverless

Custodian supports both periodic and api call events for serverless policy execution.
