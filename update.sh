#!/bin/bash
ACCOUNT=745222113226
export AWS_PROFILE=iol

docker build -t ${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/iol2/cds-service-example:latest .
cliversion=$(aws --version)
[[ $cliversion = aws-cli/1* ]] && aws ecr get-login --no-include-email --region us-east-1 | source /dev/stdin
[[ $cliversion = aws-cli/2* ]] && aws ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com
docker push ${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/iol2/cds-service-example:latest

unset AWS_PROFILE