import json
import requests
import boto3
import os
import decimal
from boto3.dynamodb.conditions import Key, Attr
import qnalib

# - Lambda hook to query the doublemap API, and construct return messages.
# - Author: sunnyc@
# - Date: 07/30/19



def handler(event, context):
    
    print(json.dumps(event))
    
    

    # - Extracting the stop name from the event args (This is set in the content designer, and must match case)
    stopName = event["res"]["result"]["args"][0]
    
    # - Query DynamoDB for the stop ID, which we will use to query the doublemap API.
    stopID = getStopIDfromName(stopName)
    
    # - Query the ETA service with the requested Stop.
    etas = getETAfromStopID(stopID) 
    
    response = ''
    

    markdown = "|  |{}|\n|:------------|:-----------------:|-------:|\n|   Bus # |   Bus Route  |ETA |".format(stopName)
    
    # - Construct the ETA Message for each arrival returned by the API.
    for arrivals in etas:
        if arrivals['bus']:
           markdown +=  "\n|    {}      |  {}      | {}      |".format(getBusNamebyID(arrivals['bus']),getRouteNamebyID(arrivals['route']),arrivals['avg'])
           response = response + ("Bus {} traveling on route {} will arrive in approximately {} minutes. ".format(str(getBusNamebyID(arrivals['bus'])), str(getRouteNamebyID(arrivals['route'])), str(arrivals['avg'])) )
           

    
    # - Set the response message in the event object, and return the event.
    
    if response:
        
        ssml = response
        text = response + "Bus scheduling information can be found here: https://bit.ly/319ECfO"
        qnalib.markdown_response(event,markdown) 
        qnalib.text_response(event,text)
        qnalib.ssml_response(event,ssml)
    
    else:
        inactive_route_text = "No buses are currently scheduled for this stop. bus stop information can be found here: https://bit.ly/319ECfO "
        inactive_route_ssml = "No buses are currently scheduled for this stop"
        
        qnalib.markdown_response(event,inactive_route_text) 
        qnalib.text_response(event,inactive_route_text)
        qnalib.ssml_response(event,inactive_route_ssml)
        
        

    return event
    
    
   
def getStopIDfromName(name):
    
    table = boto3.resource('dynamodb').Table(os.environ['STOPS'])
    
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
    try:
        busName = response['Items'][0]['name']
    except IndexError:
        busName = 'unavailable'
        
    
    # - Return the bus name.
    return busName

def getRouteNamebyID(routeID):
    
    table = boto3.resource('dynamodb').Table(os.environ['ROUTES'])

    # - Query the slu-bus-routes table for the route name. 
    response = table.query(
        KeyConditionExpression=Key('id').eq(routeID)
        )
    try:
        routeName = response['Items'][0]['name']
    except IndexError:
        routeName = "unavailalbe"
    
    
    return routeName