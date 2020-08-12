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
# 弹性云服务CVM
TENCENT_SECRETID=xxxx 
TENCENT_SECRETKEY=xxxx
TENCENT_DEFAULT_REGION=xxxx
custodian run -s . policy.yml
```
```
# 对象存储服务COS
TENCENT_SECRETID=xxxx 
TENCENT_SECRETKEY=xxxx
TENCENT_DEFAULT_REGION=xxxx
TENCENT_ENDPOINT=xxxx
custodian run -s . policy.yml
```


# Serverless

Custodian supports both periodic and api call events for serverless policy execution.
