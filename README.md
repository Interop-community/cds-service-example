# cds-service-example-python

Simple Python and Flask server that acts as a CDS Service

## To build and run locally
This card service can be deployed with docker. By default, the Dockerfile exposes port 5000. Creating the docker container can be done by:

```bash
$ docker build -t <your-name>/cds-service-example-python .
Successfully built <container-id>

$ docker run -p 5000:5000 -d --rm <your-name>/cds-service-example-python
```

# To build and push to ECR

## Create image repo in ECR 

```
aws ecr create-repository --repository-name iol2/cds-service-example 
```

## Build Docker Image

```
docker build -t 745222113226.dkr.ecr.us-east-1.amazonaws.com/iol2/cds-service-example:latest .
```


## Login to ECR from Docker cli

```
cliversion=$(aws --version)
[[ $cliversion = aws-cli/1* ]] && aws ecr get-login --no-include-email --region us-east-1 | source /dev/stdin
[[ $cliversion = aws-cli/2* ]] && aws ecr get-login-password --profile $1| docker login --username AWS --password-stdin  ${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com
```

## Push Docker Image to AWS ECR with tag
```
docker push 745222113226.dkr.ecr.us-east-1.amazonaws.com/iol2/cds-service-example:latest
```

## Automated above steps 

```
./update.sh

```
