var fs=require('fs')

module.exports={
    "LexBuildCodeVersion":{
        "Type": "Custom::S3Version",
        "DependsOn":["CFNLambdaPolicy"],
        "Properties": {
            "ServiceToken": { "Fn::GetAtt" : ["CFNLambda", "Arn"] },
            "Bucket": {"Ref":"BootstrapBucket"},
            "Key": {"Fn::Sub":"${BootstrapPrefix}/lambda/lex-build.zip"},
            "BuildDate":(new Date()).toISOString()
        }
    },
    "LexBuildLambda": {
      "Type": "AWS::Lambda::Function",
      "Properties": {
        "Code": {
            "S3Bucket": {"Ref":"BootstrapBucket"},
            "S3Key": {"Fn::Sub":"${BootstrapPrefix}/lambda/lex-build.zip"},
            "S3ObjectVersion":{"Ref":"LexBuildCodeVersion"}
        },
        "Environment": {
            "Variables": {
                UTTERANCE_BUCKET:{"Ref":"AssetBucket"},
                STAUTS_BUCKET:{"Ref":"BuildStatusBucket"},
                UTTERANCE_KEY:"default-utterances.json"
            }
        },
        "Handler": "index.handler",
        "MemorySize": "128",
        "Role": {"Fn::GetAtt": ["LexBuildLambdaRole","Arn"]},
        "Runtime": "nodejs6.10",
        "Timeout": 300,
        "Tags":[{
            Key:"Type",
            Value:"Api"
        }]
      }
    },
    "LexBuildInvokePolicy": {
      "Type": "AWS::IAM::ManagedPolicy",
      "Properties": {
        "PolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [{
              "Effect": "Allow",
              "Action": [
                "lambda:InvokeFunction"
              ],
              "Resource":[
                {"Fn::GetAtt":["LexBuildLambda","Arn"]}
              ]
            }]
        },
        "Roles": [{"Ref": "LexBuildLambdaRole"}]
      }
    },
    "LexBuildLambdaRole": {
      "Type": "AWS::IAM::Role",
      "Properties": {
        "AssumeRolePolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "lambda.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
          ]
        },
        "Policies":[{
            PolicyName:"AssetBucketAccess",
            PolicyDocument:{
                "Version" : "2012-10-17",
                "Statement": [ {
                    "Effect": "Allow",
                    "Action": ["s3:Get*"],
                    "Resource":[
                        {"Fn::Sub":"arn:aws:s3:::${AssetBucket}*"}
                    ]
                },]
            }
        }],
        "Path": "/",
        "ManagedPolicyArns": [
          "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
          {"Ref":"EsPolicy"},
          "arn:aws:iam::aws:policy/AmazonLexFullAccess"
        ]
      }
    },
    "BuildStatusBucket":{
        "Type" : "AWS::S3::Bucket",
        "Properties":{
            LifecycleConfiguration:{
                Rules:[{
                    NoncurrentVersionExpirationInDays:1,
                    Status:"Enabled"
                },{
                    AbortIncompleteMultipartUpload:{
                        DaysAfterInitiation:1
                    },
                    Status:"Enabled"
                }]
            },
            "VersioningConfiguration":{
                "Status":"Enabled"
            }
        }
    },
    "BuildStatusClear":{
        "Type": "Custom::S3Clear",
        "DependsOn":["CFNLambdaPolicy","CFNInvokePolicy"],
        "Properties": {
            "ServiceToken": { "Fn::GetAtt" : ["CFNLambda", "Arn"] },
            "Bucket":{"Ref":"BuildStatusBucket"}
        }
    }
}

