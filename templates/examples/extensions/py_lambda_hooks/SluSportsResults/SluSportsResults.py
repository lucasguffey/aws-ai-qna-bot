import json
import qnalib 
import feedparser

def handler(event, context):
    event_results = event["res"]["result"]
    sport_type  = event_results["args"][0]
    team_endpoint = feedparser.parse('http://www.slubillikens.com/rss.dbml?db_oem_id=27200&media=results&RSS_SPORT_ID={}'.format(sport_type))
    print(team_endpoint)
    if team_endpoint.get('feed') and team_endpoint.get('entries'):
        game_information = team_endpoint['entries'][0]['title']
        
    
    
    
        outcome = game_information[-7]    
        if outcome == 'L':
            game_response = game_information.replace('L','Lost')
        elif outcome == 'W':
            game_response = game_information.replace('W','Won')
        elif outcome == 'T':
            game_response = game_information.replace('T','Tied')
        else:
            qnalib.ssml_response(event,spoken_response(game_information))
            event['res']['message'] = "I am Unable to retreive the results for the scores right now. Please visit slubillikens.com for results on all sporting events."
            return event

        
        qnalib.markdown_response(event,game_response)
        qnalib.ssml_response(event,spoken_response(game_information))
        qnalib.text_response(event,game_response)
        

        
    else:

        event['res']['message'] = "I am Unable to retreive the results for the scores right now. Please visit slubillikens.com for results on all sporting events."

    return event
        
def spoken_response(result):
    team_names = result[:result.find('(') -1]
    slu_score = result[-4]
    slu_name = team_names.split('vs')[:-2]
    opponent_score = result[-2]
    opponent_name = team_names.split('vs')[1]
    if result[-7] == 'L':
        outcome = 'Lost'
    elif result[-7] == 'W':
        outcome = 'Won'
    elif result[-7] == 'T':
        outcome = 'Tied'
    else:
        outcome = None

    
    if outcome == 'Won' or outcome == 'Tied':
        alexa_response = "saint louis university {} {} against {} with the a score of {} to {}".format(slu_name,outcome,opponent_name,slu_score,opponent_score)
    elif outcome == "Lost":
        alexa_response = "saint louis university {} {} against {} with a score of {} to {}".format(slu_name,outcome,opponent_name,opponent_score,slu_score)
    else:
        alexa_response = "I am Unable to retreive the results for the scores right now. Please visit slubillikens.com for results on all sporting events."
    
    return alexa_response