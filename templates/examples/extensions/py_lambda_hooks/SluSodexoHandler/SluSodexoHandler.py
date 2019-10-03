import json
import requests
import qnalib 
import time
from jose import jwt
from secrets import get_secret


def handler(event, context):
    global token

    event_results = event["res"]["result"]
    dietary_argument = event_results["args"][0]
    meal_argument = event_results["args"][1]
    
    try:
        allergen_argument = event_results["args"][2]
    except IndexError:
        allergen_argument = None
        
    
    #if token is expired fetch a new one
    if time.time() > token['expiration']:
        token = fetch_token(password)
        
    sodexo_endpoint = requests.get("http://api-staging.sodexomyway.net/api/v1/menus/13341001/14759/{}/{}".format(dietary_argument,allergen_argument),headers={'Authorization': 'Bearer ' + token['tokenValue']})
    try:
        sodexo_endpoint.raise_for_status()
    except Exception as exc:
        event['res']['message'] = "Unable to locate the information at this time, please try again"
        return(event)
        
    menu_items = sodexo_endpoint.json()
    print(json.dumps(event))

    meals = []
    for item in menu_items['data']['menuItems']:
        if item['Meal'].lower() == meal_argument.lower():
            meals.append(item['Name'])
     


    ssml = ""
    if allergen_argument:
        markdown = "| Grand Dining Hall {} Free {} Items |\n|------------|-------|".format(allergen_argument.capitalize(),meal_argument.capitalize())
    else:
        markdown = "| Grand Dining Hall {} {} Items |\n|------------|-------|".format(dietary_argument.capitalize(),meal_argument.capitalize())
    
    if meals:    
        for i in meals:
            markdown += "\n| {}      |".format(i)
            ssml += " and {}".format(i)
        
        #response objects
        qnalib.markdown_response(event,markdown)
        if allergen_argument:
            allergen_response = written_allergen(meals,meal_argument,allergen_argument)
            qnalib.text_response(event,allergen_response)
            qnalib.ssml_response(event,allergen_response)
        
        else:
            written_response = written_restriction(meals,meal_argument,dietary_argument)
            qnalib.text_response(event,written_response)
            qnalib.ssml_response(event,written_response)
            
        return event
    else:
        event['res']['message'] = "There are currently no meals that meet this criteria"
        return event


def written_allergen(meal_list,meal_type,allergen):
        #Text and SSML response flow
    if len(meal_list) == 0 :
        response = "There are currently no {} meals right now that are {} free".format(meal_type,allergen)
    elif len(meal_list) == 1:
        response_message = "The following {} meal is {} free: ".format(meal_type,allergen)
        response = response_message + "".join(str(x) for x in meal_list)
    else:
        meal_list.insert(-1,', and')
        response_message = "The following {} meals are {} free: ".format(meal_type,allergen)
        response = response_message + ", ".join(str(x) for x in meal_list[:-2]) + " ".join(str(x) for x in meal_list[-2:])
    return response

 
def written_restriction(meal_list,meal_type,meal_restriction):  
    if len(meal_list) == 0:
        response = "There are currently no {} meals right now that are {}".format(meal_type,meal_restriction)
    elif len(meal_list) == 1:
        response_message = "The following {} meal is {}: ".format(meal_type,meal_restriction)
        response = response_message + "".join(str(x) for x in meal_list)
    else:
        meal_list.insert(-1,', and')
        response_message = "The following {} meals are {}: ".format(meal_type,meal_restriction)
        response = response_message + ", ".join(str(x) for x in meal_list[:-2]) + " ".join(str(x) for x in meal_list[-2:])
    return response
        
#fetches token from sodexo authentication server
def fetch_token(password):
        response = requests.post('http://api-staging.sodexomyway.net/api/authenticate', json={"Username":"slu.iot","Password":password['Sodexo']})
        json_response = response.json()
        claims = jwt.get_unverified_claims(json_response['token'])
        expiration = claims['exp']
        response_object = {'tokenValue':json_response['token'],'expiration':expiration}
        return response_object

password = get_secret()
token = fetch_token(password)