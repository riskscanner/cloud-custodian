echo "构建custodian镜像 ..."
docker build -t registry.fit2cloud.com/riskscanner/custodian:riskscanner .
docker push registry.fit2cloud.com/riskscanner/custodian:riskscanner