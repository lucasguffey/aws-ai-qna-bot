import json
import boto3
from botocore.exceptions import ClientError
import csv
import sys
question_file =sys.argv[1]

client = boto3.client('lex-runtime')


with open(question_file) as json_file: 
    data = json.load(json_file)

count = 0
with open('slu_bot_test_final.csv', mode='w') as output_file:
    result_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    result_writer.writerow(['Question','Expected Answer','Returned Answer','Matching Results'])
    
    for question_list in data['qna']:
        for question in question_list['q']:
            if question and question != "Feedback":
                
                try:
                    
                    response = client.post_text(
                        botName='QnABot_BotuU',
                        botAlias='BotAliasuNEMDrs',
                        userId='automated-tester1',
                        inputText=question)
                except ClientError as e:
                    print("unexpected error: {} in question {}".format(e,question))
                    
                    
                original_question = question.encode('utf-8')
                desired_response = question_list['a'].encode('utf-8')
                lex_response = response['message'].encode('utf-8')
                    
                    
                if question_list['a'] == response['message']:
                    result_matches = 'Yes'
                else:
                    result_matches = 'No'
                count+=1
                print('Processing question # {}'.format(count))
                result_writer.writerow([original_question,desired_response,lex_response,result_matches])
output_file.close()

