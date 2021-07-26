echo "构建custodian镜像 ..."

docker build -t registry.cn-qingdao.aliyuncs.com/x-lab/custodian:1.4 .
docker push registry.cn-qingdao.aliyuncs.com/x-lab/custodian:1.4
