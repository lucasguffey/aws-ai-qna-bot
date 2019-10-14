import json
import requests
import os
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
import qnalib
import re
import datetime
from datetime import date
import calendar
from datetime import datetime as dt
from pytz import timezone


def handler(event, context):
    
    response = ''
    event_results = event["res"]["result"]
    building_arg = event_results["args"][0]
    question_utterance = event["req"]["question"]
    initialmessage = ''
    my_date = date.today()
    central_object = timezone('US/Central')
    central_time = central_object.fromutc(dt.now())
    todaysDay = calendar.day_name[central_time.weekday()]
    
    
    dayOfWeek = searchUtteranceforDoW(question_utterance)
    
    if(dayOfWeek == None): 
        dayOfWeek = todaysDay
    
   # - Extracting the building name from the event args (This is set in the content designer, and must match case)
    buildingName = event["res"]["result"]["args"][0]
    
    # - Query DynamoDB for the stop ID, which we will use to query the doublemap API.
    buildingID = getBuildingIDfromName(buildingName)
    scheduleID = getScheduleIDfromBuildingID(buildingID)
    daysfromSchedule = getDaysfromScheduleID(scheduleID)
    
    
    # - Initialize the markdown values.
    markdown = "|   Day  |   Opens  |Closes |\n|:------------|:-----------------:|-------:|"
    
    # - Construct the days message.
    for days in daysfromSchedule:
        
        #openHrsConverted = dt.strptime(str(days['open']), '%H:%M').strftime('%I:%M %p')
        #print(openHrsConverted)
        # - Initialize the short response. 
        if(expandDayfromShortName(days['days']) == dayOfWeek):
            if(days['isclosed']):
                initialmessage = "On {} the {} is closed\n, here are the hours for the week:\n ".format(str(expandDayfromShortName(days['days'])), buildingName)
            else :
                initialmessage = "On {} the {} is open from {} to {}\n, here are the hours for the week:\n ".format(str(expandDayfromShortName(days['days'])), buildingName, dt.strptime(str(days['open']), '%H:%M').strftime('%I:%M %p'), dt.strptime(str(days['closed']), '%H:%M').strftime('%I:%M %p'))

        
        if days['days']:
            if(days['isclosed']):
                markdown +=    "\n|    {0}      |  Closed      | Closed      |".format(str(expandDayfromShortName(days['days'])))            
            else:
                markdown +=    "\n|    {0}      |  {1}      | {2}      |".format(str(expandDayfromShortName(days['days'])), dt.strptime(str(days['open']), '%H:%M').strftime('%I:%M %p'), dt.strptime(str(days['closed']), '%H:%M').strftime('%I:%M %p'))


        response =  initialmessage 
    
    # - Set the response message in the event object, and return the event.
    
    if response:
        # markdown = initialmessage + " following are the hours for the week \n" +  markdown 
        markdown = "{} \n{}".format(initialmessage, markdown)
        ssml = response 
        text = response 
        qnalib.markdown_response(event,markdown) 
        qnalib.text_response(event,text)
        qnalib.ssml_response(event,ssml)
    
    else:
        inactive_building_text = "Building open hours can be found here http://slu.edu"
        inactive_schedule_ssml = "No buildings are open today"
        
        qnalib.markdown_response(event,inactive_building_text) 
        qnalib.text_response(event,inactive_building_text)
        qnalib.ssml_response(event,inactive_schedule_ssml)
        
        

    return event
    
# - Search the utterance value for the day of the week. If there are other patterns that users are invoking, populate the corresponding pattern array.

def searchUtteranceforDoW(utterance):
    
    patterns = [' monday ', ' mon ']
    
    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Monday"

    patterns = [' tuesday ', ' tue ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Tuesday"

    patterns = [' wednesday ', ' wed ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Wednesday"

    patterns = [' thursday ', ' thu ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Thursday"

    patterns = [' Friday ', ' fri' ]

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Friday"

    patterns = [' Saturday ', ' sat ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Saturday"
            
    patterns = [' Sunday ', 'sun']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Sunday"

    return None



    
    
# - Pull the Daily Schedule 
def getDaysfromScheduleID(scheduleID):

    table = boto3.resource('dynamodb').Table(os.environ['DAY'])
    daysarray =[]
    
    # - Query the Schedule table for the ScheduleID.
    response = table.scan(
        FilterExpression=Key('dayScheduleId').eq(scheduleID) 
 
        )
    

    try:
        #print(response)
        for i in response['Items']:
            days =   {
                "order":  i["order"],
                "days":  i['day_name'],
                "open":    i['opening_time'],
                "closed":  i['closing_time'],
                "isclosed": i['closed']
                
            }
            daysarray.append(days)  
            
            # Sort the days by their order in the DB.
            dayssorted  = sorted(daysarray, key=lambda days: days['order'])
            
  
    except IndexError:
        scheduleID = 'unavailable'
        
    
 
    # - Return the schedule ID.
    return dayssorted


# Query the Schedule ID from the building.
def getScheduleIDfromBuildingID(buildingID):

   # print (buildingID)
    current_date = dt.now()
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    print(current_date)
    
    table = boto3.resource('dynamodb').Table(os.environ['SCHEDULE'])

    # - Query the Schedule table for the ScheduleID.
    response = table.scan(
        FilterExpression=Key('scheduleBuildingId').eq(buildingID)
        )
    print(json.dumps(response))
    
    for i in response["Items"]:
        end_date = dt.strptime(i["end_date"], '%a %b %d %Y')
        start_date = dt.strptime(i["start_date"], '%a %b %d %Y')
        print(start_date)
        print(end_date)
        if start_date <= current_date <= end_date:
            scheduleID = i["id"]
            print(scheduleID)
            return scheduleID

        else:
            scheduleID = 'unavailable'
            print('hell0 ' + scheduleID)
    return scheduleID

    try:
        scheduleID = response['Items'][0]['id']
    except IndexError:
        scheduleID = 'unavailable'
        
    
    # - Return the schedule ID.
    return scheduleID


# - Parse the building ID from the arg name.
def getBuildingIDfromName(name):

    table = boto3.resource('dynamodb').Table(os.environ['BUILDING'])
    
    # - Note: This scan is case sensitive, so make sure the QnABot arg case matches the DB. 
    response = table.scan(
	    FilterExpression=Attr('name').contains(name),
        ProjectionExpression='id', Limit=100) #Limiting the maximum number of responses to evaluate to 100
    
    # - Return the Building ID    
    response_items = response['Items'][0]['id']

    return response_items


# - Expand the short day names from the DB, to human readable values.
def expandDayfromShortName(dayName):
    
    if dayName == "Mon":
        return "Monday"
    if dayName =="Tue":
        return "Tuesday"
    if dayName == "Wed":
        return "Wednesday"
    if dayName =="Thu":
        return "Thursday"
    if dayName == "Fri":
        return "Friday"
    if dayName == "Sat":
        return "Saturday"
    if dayName == "Sun":
        return "Sunday"