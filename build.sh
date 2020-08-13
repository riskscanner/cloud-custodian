echo "构建custodian镜像 ..."
docker build -t registry.fit2cloud.com/fit2cloud2/custodian:base .
docker push registry.fit2cloud.com/fit2cloud2/custodian:base