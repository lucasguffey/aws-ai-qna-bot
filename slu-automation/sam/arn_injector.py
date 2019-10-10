import json
import sys
import re

#hydrates qna_lambda.json
def jsonInjector(feedback, sodexo, bus, allergen):
    with open('qna_lambda.json', 'r+') as f:
        data = json.load(f)
        for item in data['qna']:
            if 'Feedback' in item['qid'] and item['l']:
                item['l'] = feedback[1:-1]
            elif 'sodexo' in item['qid'] and item['l']:
                item['l'] = sodexo[1:-1]
            elif 'bus.' in item['qid'] and item['l']:
                item['l'] = bus[1:-1]
            elif 'grand.' in item['qid'] and item['l']:
                item['l'] = allergen[1:-1]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate

jsonInjector(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
