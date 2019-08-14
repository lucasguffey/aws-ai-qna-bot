import json
#import requests
from botocore.vendored import requests
import boto3
import os
import decimal
from boto3.dynamodb.conditions import Key, Attr

# - Lambda hook to query the doublemap API, and construct return messages.
# - Author: sunnyc@
# - Date: 07/30/19



def bushandler(event, context):
    
    #print(json.dumps(event))
    
    # - Setting an environment variable to allow the customer to control the initial language in the message.
    messageText = os.environ['Intro']
    
    # - Extracting the stop name from the event args (This is set in the content designer, and must match case)
    stopName = event["res"]["result"]["args"][0]
    
    # - Query DynamoDB for the stop ID, which we will use to query the doublemap API.
    stopID = getStopIDfromName(stopName)
    
    # - Query the ETA service with the requested Stop.
    etas = getETAfromStopID(stopID) 
    
    messageText = ''
    
    # - Construct the ETA Message for each arrival returned by the API.
    for arrivals in etas:
        messageText = messageText + ("Bus {} traveling on route {} will arrive in approximately {} minutes. ".format(str(getBusNamebyID(arrivals['bus'])), str(getRouteNamebyID(arrivals['route'])), str(arrivals['avg'])) )
         
    
    messageText = messageText + "Bus scheduling information can be found here: https://bit.ly/319ECfO"
    
    
    # - Set the response message in the event object, and return the event.
    if messageText:
        event["res"]["message"] = messageText
    else:
        event["res"]["message"] = "No buses currently scheduled"

    
    return event
    
    
   
def getStopIDfromName(name):
    
    table = boto3.resource('dynamodb').Table(TableName=os.environ['STOPS'])
    
    # - Note: This scan is case sensitive, so make sure the QnABot arg case matches the DB. 
    response = table.scan(
	    FilterExpression=Attr('name').contains(name),
        ProjectionExpression='id', Limit=100) #Limiting the maximum number of responses to evaluate to 100
    
    # - Return the StopID    
    response_items = response['Items'][0]['id']

    return response_items
    
    

def getETAfromStopID(stopID):    

    #print(stopID)
    
    # - Query the ETA service with the Stop ID
    requestETA = requests.get("http://slu.doublemap.com/map/v2/eta?stop={}".format(stopID))
    busarray =[]
    busstop = str(stopID)
    
    # - Construct the eta object from the request.
    eta = requestETA.json()
    
    # - Parse the eta object, and construct an array of buses.
    
    for i in eta['etas'][busstop]['etas']:
        bus =   {
                "bus":  i['bus_id'],
                "route":    i['route'],
                "avg":  i['avg']
            }
        busarray.append(bus)        
    
    return busarray
    
def getBusNamebyID(busID):

    table = boto3.resource('dynamodb').Table(os.environ['BUSES'])

    # - Query the slu-buses table for the bus name.
    response = table.query(
        KeyConditionExpression=Key('id').eq(busID)
        )
        
    busName = response['Items'][0]['name']
    
    # - Return the bus name.
    return busName

def getRouteNamebyID(routeID):
    
    table = boto3.resource('dynamodb').Table(os.environ['ROUTES'])

    # - Query the slu-bus-routes table for the route name. 
    response = table.query(
        KeyConditionExpression=Key('id').eq(routeID)
        )
        
    routeName = response['Items'][0]['name']
    
    
    return routeName