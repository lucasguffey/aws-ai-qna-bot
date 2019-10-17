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
    print("start of new function ##########################################")
    print(json.dumps(event))
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
    elif(dayOfWeek == "Tomorrow"):
        dayOfWeek = calendar.day_name[(central_time + datetime.timedelta(days=1)).weekday()]
    

    
    # - Extracting the building name from the event args (This is set in the content designer, and must match case)
    buildingName = event["res"]["result"]["args"][0]
    
    # - Query DynamoDB for the stop ID, which we will use to query the doublemap API.
    buildingID = getBuildingIDfromName(buildingName)
    day_in_dt = day_to_dt_converter(todaysDay,dayOfWeek,central_time)
    scheduleID = getScheduleIDfromBuildingID(buildingID,day_in_dt)
    day_query = getDaysfromScheduleID(scheduleID,dayOfWeek)
    if isinstance(day_query, list):
        queried_day = day_query[0]
    else:
        queried_day = day_query
        


        
    
    if queried_day == "unavailable" and todaysDay == dayOfWeek:
        initialmessage = "I cant find the hours for the {} building today.\n".format(buildingName)
    elif queried_day == "unavailable":
        initialmessage = "I cant find the hours for the {} building on {}. \n".format(buildingName,dayOfWeek)
        
    elif(queried_day['isclosed'] and todaysDay == dayOfWeek):
        initialmessage = "Today the {} is closed\n ".format(buildingName)
        
    elif queried_day['isclosed']:
        initialmessage = "On {} the {} is closed\n ".format(str(expandDayfromShortName(queried_day['days'])), buildingName)
        
    elif todaysDay == dayOfWeek:
        initialmessage = "Today the {} is open from {} to {}\n".format(buildingName, dt.strptime(str(queried_day['open']), '%H:%M').strftime('%I:%M %p'), dt.strptime(str(queried_day['closed']), '%H:%M').strftime('%I:%M %p'))
    else:
        initialmessage = "On {} the {} is open from {} to {}\n".format(str(expandDayfromShortName(queried_day['days'])), buildingName, dt.strptime(str(queried_day['open']), '%H:%M').strftime('%I:%M %p'), dt.strptime(str(queried_day['closed']), '%H:%M').strftime('%I:%M %p'))
    
    
    # - Initialize the markdown values.
    markdown = ''
    if event["req"]["_type"] != "ALEXA" and event["req"]["_event"]["requestAttributes"] == None:
        weekday_dict = dict(zip(calendar.day_name,range(7)))
        todays_number = weekday_dict[dayOfWeek]
        for i in range(todays_number,todays_number + 7):
            dt_object = day_to_dt_converter(todaysDay,i,central_time)
            week_schedule_id = getScheduleIDfromBuildingID(buildingID,dt_object)
            dt_weekday = calendar.day_name[dt_object.weekday()]
            week_object = getDaysfromScheduleID(week_schedule_id,dt_weekday)
            if isinstance(week_object, list):
                if week_object and week_object[0]['isclosed']:
                    markdown +=    "\n|    {0}      |  Closed      | Closed      |".format(dt_weekday)
                else:
                    markdown +=    "\n|    {0}      |  {1} &nbsp; &nbsp; &nbsp; &nbsp;    | {2}      |".format(dt_weekday, dt.strptime(str(week_object[0]['open']), '%H:%M').strftime('%I:%M %p'), dt.strptime(str(week_object[0]['closed']), '%H:%M').strftime('%I:%M %p'))
        if markdown:
            markdown = "|   Day  |   Opens  |Closes |\n|:------------|:-----------------:|-------:|" + markdown

    response =  initialmessage 
    
    # - Set the response message in the event object, and return the event.
    
    if response and markdown:
        markdown = "{} \n{}".format(initialmessage, markdown)
        qnalib.markdown_response(event,markdown)
    elif response:
        ssml = response 
        text = response 
        qnalib.text_response(event,text)
        qnalib.ssml_response(event,ssml)
    
    elif markdown:
        qnalib.markdown_response(event,inactive_building_text) 
    else:
        inactive_building_text = "Building open hours can be found here http://slu.edu"
        inactive_schedule_ssml = "No buildings are open today"
        qnalib.text_response(event,inactive_building_text)
        qnalib.ssml_response(event,inactive_schedule_ssml)
        
        

    return event
    
# - Search the utterance value for the day of the week. If there are other patterns that users are invoking, populate the corresponding pattern array.

def searchUtteranceforDoW(utterance):
    
    patterns = ['monday', ' mon ']
    
    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Monday"

    patterns = ['tuesday', ' tue ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Tuesday"

    patterns = ['wednesday', ' wed ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Wednesday"

    patterns = ['thursday', ' thu ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Thursday"

    patterns = ['friday', ' fri' ]

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Friday"

    patterns = ['saturday', ' sat ']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Saturday"
            
    patterns = ['Sunday', 'sun']

    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Sunday"
            
    patterns = ['tomorrow']
    
    for pattern in patterns:
        if re.search(pattern, utterance.lower()):
            return "Tomorrow"

    return None


    
    
# - Pull the Daily Schedule 
def getDaysfromScheduleID(scheduleID,dayOfWeek):
    
    if scheduleID == "unavailable":
        return "unavailable"
    table = boto3.resource('dynamodb').Table(os.environ['DAY'])
    daysarray =[]
    
    # - Query the Schedule table for the ScheduleID.
    response = table.scan(
        FilterExpression=Key('dayScheduleId').eq(scheduleID) & Key('day_name').eq(dayOfWeek[:3])
 
        )


    try:
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
            return dayssorted
            
  
    except IndexError:
        dayssorted = 'unavailable'
    # - Return the schedule ID.
        return dayssorted


# Query the Schedule ID from the building.
def getScheduleIDfromBuildingID(buildingID,current_date):

   # print (buildingID)
    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    


    
    table = boto3.resource('dynamodb').Table(os.environ['SCHEDULE'])

    # - Query the Schedule table for the ScheduleID.
    response = table.scan(
        FilterExpression=Key('scheduleBuildingId').eq(buildingID)
        )
 
    

    special_schedule_id = ''
    scheduleID = ''
    nonschedule = ''
    for i in response["Items"]:
 
        central_object = timezone('US/Central')
        end_date = central_object.localize(dt.strptime(i["end_date"], '%a %b %d %Y'))

        start_date = central_object.localize(dt.strptime(i["start_date"], '%a %b %d %Y'))

        if i["default_schedule"] == False:
            if start_date <= current_date <= end_date:
                 special_schedule_id = i["id"]
                 
        if start_date <= current_date <= end_date:
            scheduleID = i["id"]
            
        else:
            nonschedule = 'unavailable'

    if special_schedule_id:
        return special_schedule_id
    elif scheduleID:
        return scheduleID
    else:
        return nonschedule
    



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
        
        
def day_to_dt_converter(todaysDay,dayOfWeek,central_time):
    weekday_dict =dict(zip(calendar.day_name,range(7)))
    todays_int = weekday_dict[todaysDay]
    if isinstance(dayOfWeek, str):
        desired_day = (weekday_dict[dayOfWeek])
    else:
        desired_day = dayOfWeek
    
    if todays_int == 0 and todays_int != desired_day:
        exact_day = central_time + datetime.timedelta(days=desired_day)

    elif todays_int != 0 and todays_int > desired_day:
        day_delta = 7 - todays_int + desired_day
        exact_day = central_time + datetime.timedelta(days=day_delta)
        
    elif todays_int != 0 and todays_int < desired_day:
        day_delta = abs(desired_day - todays_int)
        exact_day = central_time + datetime.timedelta(days=day_delta)
        
    else:
        exact_day = central_time
    return exact_day