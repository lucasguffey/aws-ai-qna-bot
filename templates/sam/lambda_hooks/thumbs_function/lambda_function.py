import json
import string
import boto3
import os
import collections
from collections import defaultdict
import botocore.response as br
import datetime

# - Lambda hook to parse feedback from the SLU chatbot. 
# - Author: sunnyc@
# - Date: 07/24/19


def feedback_handler(event, context):

    #print(json.dumps(event))
    
    
    try:
        #get the Question ID (qid) of the previous document that was returned to the web client 
        if "sessionAttributes" in event["req"]["_event"]:
            stringToJson = json.loads(event["req"]["_event"]["sessionAttributes"]["previous"])
        #for Alexa
        else:
            stringToJson = json.loads(event["req"]["_event"]["session"]["attributes"]["previous"])
        previousQid = stringToJson["qid"]
        previousQuestion = stringToJson["q"]
        previousAnswer = stringToJson["a"]
        previousAlt = stringToJson["alt"]
    except:
        #replace qid with the String '' if there is no previous questions that have been asked
        previousQid = ''
    
    
    feedbackArg = event["res"]["result"]["args"][0]
    print(feedbackArg)
   
    # - Check feedbackArg from the UI payload. Parse for "thumbs_down_arg" feedback. Based on user action, sendFeedback through SNS, and log in Firehose. 
    if (feedbackArg == "thumbs_down_arg") :
        sendFeedbackNotification(previousQid,previousAnswer,previousQuestion, previousAlt, feedbackArg)
        logFeedback(previousQid,previousAnswer,previousQuestion, previousAlt, feedbackArg)
    else:
        logFeedback(previousQid,previousAnswer,previousQuestion, previousAlt, feedbackArg)
        

    return event

#logs feedback for the questions
def logFeedback(qid,answer,question, alt, inputText):
    #uncomment below if you would like to see values passed in 
    jsonData = {"qid":"{0}".format(qid),
        "utterance":"{0}".format(question),
        "answer":"{0}".format(answer),
        "feedback":"{0}".format(inputText),
        "datetime":"{0}".format(datetime.datetime.now().isoformat())
    }
    jsondump=json.dumps(jsonData,ensure_ascii=False)
    client = boto3.client('firehose')
    response = client.put_record(
        DeliveryStreamName=os.environ['FIREHOSE_NAME'],
        Record={
            'Data': jsondump
        }
    )
    #uncomment below if you would like to see the response returned by the firehose stream
    #print(response)

# - Sends SNS notification for feedback.
def sendFeedbackNotification( qid,answer,question, alt, inputText):
    
    notificationBody = "\n\nTimestamp: {5} Question ID: {0}\nQuestion: {1} \nAnswer: {2} \nAlternative Answer: {3} \nFeedback: {4}".format(qid,question,answer, alt, inputText, datetime.datetime.now().isoformat())
   
    #print(notificationBody)
    message = {"qnabot": "publish to feedback topic"}
    client = boto3.client('sns')
    response = client.publish(
       
        TargetArn=  os.environ['SNS_TOPIC_ARN'], 
        Message=json.dumps({'default': notificationBody
        }),
        Subject='QnABot - Feedback received',
        MessageStructure='json'
    )