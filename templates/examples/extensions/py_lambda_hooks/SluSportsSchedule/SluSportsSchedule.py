import json
import qnalib 
import feedparser
import datetime
import calendar

def handler(event, context):
    event_results = event["res"]["result"]
    sport_type  = event_results["args"][0]
    team_endpoint = feedparser.parse('http://www.slubillikens.com/rss.dbml?db_oem_id=27200&media=schedulesxml&RSS_SPORT_ID={}'.format(sport_type))
    print(team_endpoint)
    if team_endpoint.get('feed') and team_endpoint.get('entries') :
        return_message = date_conversion(team_endpoint)
        qnalib.markdown_response(event,return_message) 
        qnalib.text_response(event,return_message)
        qnalib.ssml_response(event,return_message)
    
        return event
        
        
    else:
        event['res']['message'] = "Cannot locate schedule at this time. Please visit slubillikens.com for full sports schedule information."
        return event
        
        
def date_conversion(game_date):
    scheduled_game = game_date['entries'][0]
    date_split = scheduled_game['date'].split()
    team_name = scheduled_game['sport']
    opponent_name = scheduled_game['opponent']
    date_of_game = date_split[0]
    time_of_game = date_split[1] + date_split[2]
    converted_date = datetime.datetime.strptime(date_of_game, '%m/%d/%Y')
    day_of_week = converted_date.weekday()
    days_of_week_dict = dict(zip(range(7),calendar.day_name))

    response = 'The {} game vs {} is on {} {} at {}'.format(team_name,opponent_name,days_of_week_dict[day_of_week], date_of_game, time_of_game)
    return response
    