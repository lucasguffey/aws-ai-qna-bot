# A Question and Answer Bot Using Amazon Lex and Amazon Alexa

> Build a chat bot to answer questions. 
Hi TOM THIS IS A CHANGE

## Overview
This repository contains code for the QnABot, described in the AWS AI blog post [“Creating a Question and Answer Bot with Amazon Lex and Amazon Alexa”](https://aws.amazon.com/blogs/ai/creating-a-question-and-answer-bot-with-amazon-lex-and-amazon-alexa/).

See the "Getting Started" to launch your own QnABot

**New features in 4.1.0** [Encryption at rest for S3 and Elastic Search Cluster, option to require Cognito user pool authorization to access embedded web UI, enhanced Kendra integration, enhanced Connect integration, and others](#new-features)

**New features in 4.0.0** [Update to Elasticsearch 7.4, improved question matching accuracy, fuzzy matching, new multi-language support debug setting, SSML for Amazon Connect, improved Kendra integration, full upgrade support](#new-features)

**New features in 3.0.3** [New content tuning Readme, Enhanced CFN Lex Resource to work with manually created Bot versions](#new-features)

**New features in 3.0.2** [New Elicit Response Bots, Lambda Functions backing conditional chaining, Lex Bot versioning use](#new-features)

**New features in 3.0.0** [ElicitResponse, Conditional Chaining, new Launch regions](#new-features)

## Upgrade Notes
During an upgrade, we recommend that existing QnABot content first be exported and downloaded from the Content Designer prior to 
the upgrade. In this release we expect upgrade to be smooth but just in case you should always have your QnABot content preserved. 

## Prerequisites

- Run Linux. (tested on Amazon Linux)
- Install npm >6.13.1 and node >10.16.3. ([instructions](https://nodejs.org/en/download/))
- Clone this repo.
- Set up an AWS account. ([instructions](https://AWS.amazon.com/free/?sc_channel=PS&sc_campaign=acquisition_US&sc_publisher=google&sc_medium=cloud_computing_b&sc_content=AWS_account_bmm_control_q32016&sc_detail=%2BAWS%20%2Baccount&sc_category=cloud_computing&sc_segment=102882724242&sc_matchtype=b&sc_country=US&s_kwcid=AL!4422!3!102882724242!b!!g!!%2BAWS%20%2Baccount&ef_id=WS3s1AAAAJur-Oj2:20170825145941:s))
- Configure AWS CLI and a local credentials file. ([instructions](http://docs.AWS.amazon.com/cli/latest/userguide/cli-chap-welcome.html))  


## Getting Started
Two approaches can be used to get started. Deploy from pre-created repositories or clone the repo and build a version yourself.

### Pre-created deployment 
Click a button to launch QnABot CloudFormation stack in the desired region

| Region   |  Launch | 
|----------|:-------------:|
| Northern Virginia | <a target="_blank" href="https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=QnABot&templateURL=http://aws-bigdata-blog.s3.amazonaws.com/artifacts/aws-ai-qna-bot/templates/public.json"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a>     |
| Oregon | <a target="_blank" href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=QnABot&templateURL=http://aws-bigdata-blog-replica-us-west-2.s3.us-west-2.amazonaws.com/artifacts/aws-ai-qna-bot/templates/public.json"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |
| Ireland | <a target="_blank" href="https://eu-west-1.console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=QnABot&templateURL=https://aws-bigdata-blog-replica-eu-west-1.s3-eu-west-1.amazonaws.com/artifacts/aws-ai-qna-bot/templates/public.json"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |
| Sydney | <a target="_blank" href="https://ap-southeast-2.console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/new?stackName=QnABot&templateURL=https://aws-bigdata-blog-replica-ap-southeast-2.s3-ap-southeast-2.amazonaws.com/artifacts/aws-ai-qna-bot/templates/public.json"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |

### Clone the git repo and build a version
First, install all prerequisites:
```shell
npm install 
```

Next, set up your configuration file:

```shell
npm run config
```

now edit config.json with you information.

| param | description | 
|-------|-------------|
|region | the AWS region to launch stacks in |
|profile| the AWS credential profile to use |
|namespace| a logical name space to run your templates in such as dev, test and/or prod |
|devEmail(required) | the email to use when creating admin users in automated stack launches |

Next, use the following command to launch a CloudFormation template to create the S3 bucket to be used for lambda code and CloudFormation templates. Wait for this template to complete (you can watch progress from the command line or [AWS CloudFormation console](https://console.AWS.amazon.com/cloudformation/home))  
```shell
npm run bootstrap
```

Finally, use the following command to launch template to deploy the QnA bot in your AWS account. When the stack has completed you will be able to log into the Designer UI (The URL is an output of the template). A temporary password to the email in your config.json:
```shell
npm run up
```

If you have an existing stack you can run the following to update your stack:
```shell 
npm run update
```

## Components
### CloudFormation Templates
The CloudFormation test templates are in the templates/test folder. The current templates are:

1. Master: the template contains all the resources for QnABot.
2. Public: this is a version of the Master template with less parameters, less outputs, and the bootstrap bucket hardcoded to the publicBucket in config.json
3. various templates in /templates/dev: needed for local testing of the lambda functions. 

Run a template test with:
```shell
npm run stack test/{template-name}
```

For example, if you want to test the domain template run:
```shell
npm run stack test/domain
```

To understand the command more run: 
```shell 
npm run stack -h
```

You also can check a template's syntax with:
```shell
npm run check {template-name}
```
ex. 
```shell
npm run check domain
```

To understand the command more run: 
```shell 
npm check stack -h
```

### Lambda Functions
Lambda functions are found in the /lambda directory. Refer to the README.md file in each directory for instructions on setting up a dev environment and testing. 
[Fulfillment](lambda/fulfillment/README.md)
[CFN](lambda/handler/README.md)
[Lex-Build](lambda/lex-build/README.md)
[Import](lambda/import/README.md)

### Web Interface
The Designer UI and client UI code is in the /website directory. 

To Test the web ui, Launch a development master stack:
```shell
npm run stack dev/master up
```
when that stack has finished run:
```shell
cd ./website ; make dev
```
this will launch a running webpack process that will watch for changes to files and upload the changes to your running dev/master stack. 

#### Designer UI Compatibility 
Currently the only browsers supported are:  
- Chrome  
- FireFox  
We are currently working on adding Microsoft Edge support.  

## Built With

* [Vue](https://vuejs.org/) 
* [Webpack](https://webpack.github.io/)

## License
See the [LICENSE.md](LICENSE.md) file for details

## New features 

### Version 4.1.0
- Install / Upgrade now supports the option to configure S3 Buckets and Elastic Search cluster using encryption at rest
- Install / Upgrade now supports the option to require Cognito based user authorization to access the built-in full screen web UI (Public/Private parameter in template) - Public is the default
- Added two settings parameters to enforce user identity verification check, so that bot can be secured for use by authenticated users only
    - ENFORCE_VERIFIED_IDENTITY. Default is false. Set to true to make QnABot require verified identity from client
    - NO_VERIFIED_IDENTITY_QUESTION. The default is "no_verified_identity". If user identity cannot be verified, replace question string with this. If not verified, the system will respond to user's question with the result of searching for NO_VERIFIED_IDENTITY_QUESTION. This allows a customizable message which informs the user that they must log in. A default question with qid "no_verified_identity" is included in QNAUtility example package.
- Enhanced Kendra fallback integration to use a specific answer if there is a best answer available and bold face highlighted words from Kendra response
- Added Comprehend sentiment analysis to all utterances and text captured by the QNAFreeText elicit response bot
- Enhanced Kibana dashboard to identify Lex client channels - Connect, Web, SMS
- Improved internal use of Booleans from settings configuration 
- Enhanced Connect integration 
    - Added session attribute named "qnabot_qid" that holds the matching question id found in elastic search
    - Added session attribute "qnabot_gotanswer" that holds boolean true/fale if an answer was fround
    - Encapsulating all Kendra and Elicit Response Bot session attributes into a single "qnabotcontext" attribute making it easier to store and reset in Connect contact flow
- Added new QNAYesNoExit elicit response bot which allows a user to exit the YesNoExit question using "exit", "bye", "quit", "admin", "rep","representative","stop", "help", "bye", "goodbye" which sets the Yes_No_Exit slot value / session attribute to "Exit".
- Update to 0.17.0 of embedded lex-web-ui
- Resolved additional dependabot identified security issues with dependent packages
- Fixed lambda/fulfillment unit tests
- Fixed defect where response bot was not triggered on next question when using lambda function for conditional chaining 

### Version 4.0.0
- Update to Elasticsearch 7.4
- Improved question matching accuracy and tuning
- Tolerance for typos and minor spelling errors with fuzzy matching setting
- Easier troubleshooting when using voice or multi-language support with new debug setting
- SSML support when using Amazon Connect
- Improvements to Amazon Kendra integration
- Full upgrade support without data loss when upgrading from previous versions.

### Content Tuning and Accuracy Guide
Content Tuning an and Accuracy Guide now available as a Markdown Readme.  [README](tuning_accuracy_guide/AWS_QnABot_tuning_recognition_accuracy_guide.md)

### Optional Redact feature for log and metric output
QnABot can be configured to redact information written to CloudWatch logs, S3 metrics, and Kibana metrics logs. 
This feature is disabled by default. Use the Designer UI Settings form to enable this feature. One can configure
the RegEx applied to strings as they are logged. If RegEx matches are found, the match is replaced with the string
'XXXXXX'.

The initial RegEx is 
```
\b\d{4}\b(?![-])|\b\d{9}\b|\b\d{3}-\d{2}-\d{4}\b
```

This replaces 4 digit numbers not followed by a hyphen, a 9 digit number (SSN without hyphens), and a typical
SSN using nnn-nn-nnnn syntax with hyphens. 
 
### New Connect Callback Example
New example demonstrating how QnABot can be asked by a user for a live agent based phone callback. The 
implementation provides a new LambdaHook example as well as four sample questions that ask a user for 
their name and phone number prior to handing off to an Amazon Connect instance to initiate the callback. 

**Two configuration updates are required to use this example with Amazon Connect.**

The IAM Role/Policy used by the ConnectCallback Lambda must include a new policy that allows 
the action "connect:StartOutboundVoiceContact" to be used with the resource
"arn:aws:connect:*:*:instance/<YourConnectInstanceId>/*". The following is an example of this policy
```
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Sid": "VisualEditor0",
           "Effect": "Allow",
           "Action": "connect:StartOutboundVoiceContact",
           "Resource": "arn:aws:connect:*:*:instance/<YourConnectInstanceId>/*"
       }
   ]
}
```
1) Find the Lambda ConnectCallback Function in the AWS Lambda Console
2) Open the AWS Console and select the Lambda Service
3) In the Console's filter enter 'ConnectCallback' and press enter
4) The displayed function will start with <stackname>-ExamplePYTHONLambdaConne... If you have multiple QnABot stacks
installed you'll see multiple functions listed
5) Open the Lambda function by clicking on the function
6) Select the Permissions tab
7) Click on the Role name to open this Role in a new tab
8) Click on + Add inline policy
9) Select the JSON tab
10) Copy the sample text above, paste as JSON, and change <YourConnectInstanceId> to the Instance ID identified in the Connect Console.
11) Click on Review policy
12) Enter a name for the policy and click Create policy

You've now enabled Lambda functions using this role to start outbound calls via the connect instance

Lambda Hook Arguments need to be updated. Before being used, the item with qid CONNECT_TO_AGENT.04 
should have its Arguments field adjusted to reflect identifiers from the Connect instance:
``` 
"AWS_connect_instance_id": "<your-connect-instance-id >",
"AWS_connect_contact_flow_id": "<your-connect-contact-flow-id>", 
"AWS_connect_queue_id": "<your-connect-queue-id>", 
```
Once these configuration changes are in place, QnABot can be successfully use Amazon Connect to place
outbound calls. 

### Conditional Chaining now supports Lambda Function
You can specify that a Conditional Chaining rule runs a Lambda Function using the "Lambda::FunctionName" syntax.
The Lambda function name must start with "QNA". The Lambda will receive arguments the same as Lambda Hooks. The
function must return a String that is used to resolve the next item just the same as other conditional chaining rules.

### Improved Scale
This release of QnABot utilizes Lex Bot aliases and Lex versioning. The QnA Bot and all ElicitResponse Bots are
now installed using the alias 'live'. 'live' points at the latest numbered Bot version. All Lex resources are now
versioned starting with '1' after initial installation.

### Additional Elicit Response Bots
This release adds several elicit response bots for 
QNAWage - 7 digit wage value - returns slot named "Wage"
QNASocialSecurity - SSN Numbers in the nnn-nn-nnnn format - returns slot named "SSN"
QNAPin - 4 digit pin value - Returns slot named "Pin"

### Configuring QnABot to ask the questions
QnABot was designed to answer questions, but now it can also ask questions and process 
the user’s answers. Use this feature for data collection and validation; 
or implement surveys, quizzes, personalized recommendations; or to build a triage 
chatbot application. See the [blog post](https://aws.amazon.com/blogs/machine-learning/creating-a-question-and-answer-bot-with-amazon-lex-and-amazon-alexa/) for details about this new feature. 
This feature is know as ElicitResponse from a configuration perspective.

### Automatically advancing and branching along a tree of questions
QnABot can now chain the user from one answer to another. This can be used with ElicitResponse
to ask multiple questions from a user. Conditional chaining allows branching based on 
the state of session variables. Please see the [blog post](https://aws.amazon.com/blogs/machine-learning/creating-a-question-and-answer-bot-with-amazon-lex-and-amazon-alexa/)
for a description on how to use this feature.

### Kendra Fallback Support
QnABot version 2.6.0 optionally supports integration with Amazon Kendra as a fallback mechanism if a question/answer can not
be found in QnABot.
 
**Important note. Use of Kendra as a fallback mechanism will incur additional charges for your AWS Account. Please 
review the Kendra pricing structure. The fallback mechanism for QnABot can be useful when deploying Kendra as an
Enterprise search solution.**
 
To enable this support for your Kendra indexes, use the Settings UI in the Designer and add your 
index to the ALT_SEARCH_KENDRA_INDEXS parameter. This parameter takes an array of strings and uses the form below.
```
["a672e3a2-nnnn-nnnn-nnnn-7b3abc81c313"]
```
**Don't forget to use your Kendra Index ID rather than the one in the sample**

Next use the QnABot Designer UI to import a Sample/Extension named KendraFallback.

This loads a new question with a qid of "KendraFallback". Edit this question in the Designer UI and change its question from 
"no_hits_alternative" to "no_hits" and save the changes. 

If you have previously loaded the QnAUtility.json from Examples/Extensions you need to either remove 
the question with the ID "CustomNoMatches" or change the question for this ID from "no_hits" to "no_hits_original"

Once the new question, "KendraFallback" is configured as the response for "no_hits", the Kendra index will be
searched for an answer whenever a curated answer can not be found. This feature provides a fallback mechanism
prior to telling the user an answer could not be found. 

A [workshop](https://github.com/aws-samples/aws-ai-qna-bot/tree/master/workshops/reinvent2019/readme.md) is available in github 
that will walk you through setting up this feature. 

**Important note. Use of Kendra as a fallback mechanism will incur additional charges for your AWS Account. Please 
review the Kendra pricing structure. The fallback mechanism for QnABot can be useful when deploying Kendra as an
Enterprise search solution.**

### MultiLanguage Support

QnABot version 2.6.0 supports use of multiple languages with these limitations:
- MultiLanguage support for voice is limited to use with Alexa skills only. (Amazon Lex currently supports voice recognition in English only)
- MutiLanguage support for text is available via all text clients (e.g. Lex Web UI, SMS, etc.)

 ####Lex (text mode only):  

If the user enters a question in a language other than english, QnABot will attempt to return an answer in the other language. 
It does this by using Amazon Comprehend to identify the language typed. If Comprehend can identify the language based on a configured minimum confidence, 
QnABot will serve up content based on that locale.

Users can also set a preferred language whereby QnABot will always attempt to respond with content in the chosen
locale.  If the user sets the preferred language to be Spanish, QnABot will always try and serve up content using
Spanish when possible. 

####Alexa (voice)

You will need to add each language you want to use to your QnABot skill using the Alexa Developer console. The intent schema for each 
language will be identical except for the skill invocation name. Give the skill a unique invokation name for each language that you add.

QnABot will use the language setting provided by Alexa, and will attempt to respond in that language.

####How it works

QnABot converts the question posed by the user to English, using Amazon Translate, and performs a lookup of the answer in Elastic Search 
just as it normally does, using the English translation of the question. ElasticSearch searches are done in English only since QnABot documents
are indexed using the English text analyser (stemming, stop words, etc.)

To ensure good matching of translated questions, you can use the Amazon Translate console to see the English tranlation of your local language question. Use QnABot content designer
to ensure your QnA item has the right sample questions to ensure a match.

Once it finds the question, QnABot will serve up the configured answer. 

You can use Handlebar blocks to define explicit answers in each different language you want to support. OR, if you do not 
explicitly define an answer in the user's language, QnABot will automatically use Amazon Translate to convert the default enghlish 
answer to the target language.

####Configuration

By default this feature is disabled. Use the following three steps to enable and configure this feature. Step 1 enables 
the feature. Step 2 loads in two questions from this extension that allow the user to select a preferred language. The 
defaults supplied in this question are English, Spanish, French, German, and Italian. You can extend this list to
support other languages. 

Step 1) Enable multi language support 

a) QnABot uses a property named ENABLE_MULTI_LANGUAGE_SUPPORT, default value of "false". 
You can change this setting using the Content Designer Settings page. Set it to "true" to enable multi language support.


Step 2) Use the Designer UI to import the Sample/Extension named Language / Multiple Language Support.

This will add two questions to the system: Language.000 and Language.001. When using Lex text clients, these questions will allow you to set your preferred language.  
The preferred language, if set, will take precendence over
the auto detected language.  

_When using Alexa, the language is automatically set by the skill. You will not be able to override the preferred language when using Alexa._

Language.000 provides a question that allows the user to set the current sessions preferred output saying a simple word 
such as French, German, or Spanish, or Italian. 

Language.001 resets the preferred language. This can be performed by saying or typing 'reset language' or 'detect language'. 
You can also input using your language of choice assuming AWS Translate can translate the input back to English. 

Once you've imported this extension question try typing the question 'Spanish'. You should see a Spanish response. 

Next enter 'English' and you will have switched your preference back to English. 

Next enter 'reset language' and your preference will be reset and language auto detection will occur again.

The answer for Language.000 uses the following handlebar syntax

```
{{#setLang 'fr' false}} D'accord. J'ai défini votre langue préférée sur l'anglais. {{/setLang}}
{{#setLang 'es' false}} Okay. He configurado tu idioma preferido al inglés.  {{/setLang}}
{{#setLang 'de' false}} In Ordnung. Ich habe Ihre bevorzugte Sprache auf Englisch eingestellt. {{/setLang}}
{{#setLang 'it' false}} Ok. Ho impostato la tua lingua preferita sull'inglese.{{/setLang}}
{{#setLang 'en' true}} Ok. I've set your preferred language to English. {{/setLang}}
```

The helper function setLang performs the necessary processing to set the preferred language/locale for teh session. To
add support for other languages just extend the answer in Language.000 with additional locales. 


Step 3) In order to serve up content that is locale specific you can

- allow QnABot to automatically translate your english answers to the session language using Amazon Translate.
- OR provide explicitly curated answers in QnA items, in multiple languages, using handlebars, as shown below. 

Lets modify the question sun.1. The following would be an example where the handlebar function ifLang is used to 
specify a response for spanish. 

Use the handlebar template defaultLang to specify the response QnABot should provide when the language is unknown. By
default this is typically in English but could be in any language as needed. 

{{#defaultLant}}{{/defaultLang}} must be the last element in the answer block. 

```
{{#ifLang 'es'}}
Nuestro sol tiene 4.600 millones de años. Se considera una enana amarilla con un diámetro de 1,392,684 kilómetros y una circunferencia de 4,370,005 kilómetros. Tiene una masa que es igual a 333,060 tierras y una temperatura superficial de 5,500 grados centígrados. ¡Muy caliente!
{{/ifLang}}
{{#defaultLang}}
Our sun is 4.6 billion years old. Its considered a yellow dwarf with a diameter of 1,392,684 kilometers and a circumference of 4,370,005 kilometers. It has a mass that is equal to 333,060 earths and a surface temperature of 5,500 degrees celsius. Really Hot!
{{/defaultLang}}
```

The handlebar function ifLang takes locale as a quoted parameter. This tells QnABot which locale to associate with the subsequent
text. 


A [workshop](https://github.com/aws-samples/aws-ai-qna-bot/tree/master/workshops/reinvent2019/readme.md) is available in github 
that will walk you through setting up this feature. 