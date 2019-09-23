import json
from botocore.vendored import requests
import boto3
import os

# - Purpose: Populate DynamoDB with supporting data for the SLU bus system.
# - Author: sunnyc@
# - Date: 07/30/19



def handler(event, context):

    requestStops = requests.get("http://slu.doublemap.com/map/v2/stops")
    requestBuses = requests.get("http://slu.doublemap.com/map/v2/buses")
    requestRoutes = requests.get("http://slu.doublemap.com/map/v2/routes")
    
    stops = requestStops.json()
    buses = requestBuses.json()
    routes = requestRoutes.json()
    
    dynamodb = boto3.client('dynamodb')
    
    
    for stop in stops:
        dynamodb.put_item(TableName=os.environ['STOPS'], Item={'id':{'N': json.dumps(stop["id"])},'name':{'S': json.dumps(stop["name"])},'buddy':{'S': json.dumps(stop["buddy"])} })
        #print(stop["name"])
        
    
    for bus in buses:
        dynamodb.put_item(TableName=os.environ['BUSES'], Item={'id':{'N': json.dumps(bus["id"])},'name':{'S': json.dumps(bus["name"])}, 'route':{'N': json.dumps(bus["route"])},'lastStop':{'N': json.dumps(bus["lastStop"])} })
        #print(bus["name"])
        
    for route in routes:
        stops = [str(i) for i in route["stops"]]
        dynamodb.put_item(TableName=os.environ['ROUTES'], Item={'id':{'N': json.dumps(route["id"])},'name':{'S': json.dumps(route["name"])},'stops':{'NS': stops} })
        #print(route["name"])
        
        