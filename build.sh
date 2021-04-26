echo "构建custodian镜像 ..."

docker build -t registry.cn-qingdao.aliyuncs.com/x-lab/custodian:master .
docker push registry.cn-qingdao.aliyuncs.com/x-lab/custodian:master
