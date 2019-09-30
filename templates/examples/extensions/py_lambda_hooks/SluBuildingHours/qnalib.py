
def markdown_response(event,markdown):
    event["res"]["session"]["appContext"]["altMessages"]["markdown"] = markdown

def text_response(event,text):
    if event["req"]["_type"] and event["req"]["_type"] == "ALEXA":
        if event['res']['message']:
            pass
    elif event["req"]["_event"]["outputDialogMode"] != "Text":
        pass
    else:
        event['res']['message'] = text
        
def ssml_response(event,ssml):
    if event["req"]["_type"] and event["req"]["_type"] == "ALEXA":
        event['res']['message'] = ssml
    elif event["req"]["_event"]["outputDialogMode"] != "Text":
        event['res']['message'] = ssml
    else:
        pass
    
