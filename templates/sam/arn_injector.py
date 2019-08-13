import json
import sys
import re

def jsonInjector(feedback, sodexo, bus):
    with open('qna_lambda.json', 'r+') as f:
        data = json.load(f)
        for item in data['qna']:
            if 'Feedback' in item['qid']:
                item['l'] = feedback[1:-1]
            elif 'sodexo' in item['qid']:
                item['l'] = sodexo[1:-1]
            elif 'bus.' in item['qid']:
                item['l'] = bus[1:-1]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate

jsonInjector(sys.argv[1], sys.argv[2], sys.argv[3])
