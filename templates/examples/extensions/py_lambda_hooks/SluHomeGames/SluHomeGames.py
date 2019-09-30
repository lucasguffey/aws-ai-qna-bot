import json
import qnalib 
import feedparser
import datetime
import calendar

def handler(event, context):
    schedule_endpoint = feedparser.parse('http://www.slubillikens.com/rss.dbml?db_oem_id=27200&media=schedulesxml&RSS_SPORT_ID=')
    if schedule_endpoint.get('feed') and schedule_endpoint.get('entries') :
        response_list = []
        count = 0
        for i in schedule_endpoint['entries']:
            if i['homeaway'] == 'H' and len(response_list) < 5:
                game_information = date_conversion(i)
                response_list.append(game_information)
                
    
        spoken_response_list = response_list.insert(-2,'and ')
        response_string = ''
        markdown = "| Upcoming SLU Home Games |\n|------------|-------|"
        for i in response_list:
            markdown += "\n| {}      |".format(i)
        for i in spoken_response_list:
            response_string = response_string + i
        
        qnalib.markdown_response(event,markdown) 
        qnalib.text_response(event,response_string)
        qnalib.ssml_response(event,response_string)
        
        
        return event
        
        
    else:
        event['res']['message'] = "Cannot locate schedule at this time. Please visit slubillikens.com for full sports schedule information."
        return event
        


def date_conversion(game_instance):
    date_split = game_instance['date'].split()
    team_name = game_instance['sport']
    opponent_name = game_instance['opponent']
    date_of_game = date_split[0]
    time_of_game = date_split[1] + date_split[2]
    converted_date = datetime.datetime.strptime(date_of_game, '%m/%d/%Y')
    day_of_week = converted_date.weekday()
    days_of_week_dict = dict(zip(range(7),calendar.day_name))

    response = 'The {} team vs {} will be on {} {} at {} '.format(team_name,opponent_name,days_of_week_dict[day_of_week], date_of_game, time_of_game)
    return response
    