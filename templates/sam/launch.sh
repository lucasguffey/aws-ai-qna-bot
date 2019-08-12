#!/bin/bash

# create a virtual environment with python 3 to work from within
echo "CREATING VIRTUAL ENVIRONMENT"
virtualenv -p /usr/bin/python3 vp3
source vp3/bin/activate

# checks first argument for existing bucket, if it doesn't exist create the bucket
echo "Searching for bucket $1"
if aws s3 ls "s3://$1" 2>&1 | grep -q 'NoSuchBucket'
then 
echo "No such bucket, CREATING BUCKET $1"
aws s3 mb s3://$1
fi

# packages and deploys the stack
echo "PACKAGING SAM TEMPLATE"
sam package --output-template stack.yaml --s3-bucket $1
echo "DEPLOYING SAM STACK"
sam deploy --template-file stack.yaml --region us-east-1 --capabilities CAPABILITY_IAM --stack-name $2

# wait for stack to be complete
echo "WAITING ..."
aws cloudformation wait stack-create-complete --stack-name $2

FEEDBACK="$(aws cloudformation describe-stacks --stack-name $2 --query "Stacks[0].Outputs[*].OutputValue" | grep 'feedback')"
OPEN="$(aws cloudformation describe-stacks --stack-name $2 --query "Stacks[0].Outputs[*].OutputValue" | grep 'whats-open-now')"
BUS="$(aws cloudformation describe-stacks --stack-name $2 --query "Stacks[0].Outputs[*].OutputValue" | grep 'bus-handler')"
POPULATE="$(aws cloudformation describe-stacks --stack-name $2 --query "Stacks[0].Outputs[*].OutputValue" | grep 'populate')"

# python jsonInjector(FEEDBACK, OPEN, BUS, POPULATE)
echo "Stack outputs"
echo $FEEDBACK
echo $OPEN
echo $BUS
echo $POPULATE

deactivate




