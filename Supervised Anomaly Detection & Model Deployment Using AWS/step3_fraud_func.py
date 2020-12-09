
##############################################################################
#  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                            #
#  Licensed under the Amazon Software License (the "License"). You may not   #
#  use this file except in compliance with the License. A copy of the        #
#  License is located at                                                     #
#                                                                            #
#      http://aws.amazon.com/asl/                                            #
#                                                                            #
#  or in the "license" file accompanying this file. This file is distributed #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,        #
#  express or implied. See the License for the specific language governing   #
#  permissions and limitations under the License.                            #
##############################################################################
import json
import os
import boto3
import random
import datetime
import re
import base64
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    success = 0
    failure = 0
    output=[]

    for record in event['records']:
        try:
            data_payload,true_label = get_features(record['data'])
            pred_score_n_label = get_fraud_prediction(data_payload) #return a list: [pred_proba, pred_label]
            transformed_data = postprocess_event(event, pred_score_n_label,true_label)
            print('output schema: {}'.format(transformed_data))
            #print('output_data: {}'.format(transformed_data))
            response = store_data_prediction(transformed_data)
            success+=1
            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': data_payload
            }
            output.append(output_record)
        except Exception as e:
            print(e)
            print('prediction failed')
            failure += 1
            output_record = {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            }
            output.append(output_record)

    logger.info('Processing completed.  Successful records {}, Failed records {}.'.format(success,failure))
    return {'records': output}




        #if not data_payload:
        #    return
        #pred = get_fraud_prediction(data_payload)
        #transformed_data = postprocess_event(event, pred)
        #response = store_data_prediction(transformed_data)
        #print(response)

'''
decode base64_encoded features;
reorder the features;
convert it to csv format;

'''
def get_features(payload):

    decoded_payload = str(base64.b64decode(payload),'utf-8')
    unordered_features = json.loads(decoded_payload)
    ordered_features = [unordered_features['Time']]
    for i in range(28):
        ordered_features += [unordered_features['V{}'.format(i+1)]]
    ordered_features+=[unordered_features['Amount']]

    return ','.join(map(str, ordered_features)),unordered_features['Class']


def get_fraud_prediction(data):
    threshold = 0.5
    pred_label = 0
    sagemaker_endpoint_name = 'fraud-detection-endpoint-linear-recall'
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    #print('features sent for prediction: {}'.format(data))
    #print('before prediction: {}'.format(str(datetime.datetime.now())))
    response = sagemaker_runtime.invoke_endpoint(EndpointName=sagemaker_endpoint_name, ContentType='text/csv',
                                                 Body=data)
    #print('after prediction: {}'.format(str(datetime.datetime.now())))
    result = json.loads(response['Body'].read().decode()) #it's a probability
    print('prediction results from sagemaker: {}'.format(result))
    #result = round(result,2)
    #if result > threshold:
    #    pred_label = 1

    pred_score_n_label = result['predictions'][0]
    #pred_score_n_label = {'score':result,'predicted_label':pred_label}
    #print('list: {}'.format(pred_score_n_label))
    return pred_score_n_label

def postprocess_event(event, pred_score_n_label,true_label):
    millisecond_regex = r'\.\d+'
    #timestamp = re.sub(millisecond_regex, '', str(datetime.datetime.now()))
    #timestamp = str(datetime.datetime.now())
    timestamp = datetime.datetime.now()-datetime.timedelta(hours=6)
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    source = random.choice(['Mobile', 'Web', 'Store']) #random thing here
    recordId = random.randint(1,100000)
    return [timestamp,str(recordId), source, str(pred_score_n_label['predicted_label']),str(pred_score_n_label['score']),str(true_label)]

def store_data_prediction(data):
    firehose_delivery_stream = 'fraud-detection-firehose-stream'

    firehose = boto3.client('firehose', region_name=os.environ['AWS_REGION'])
    record = ','.join(data) + '\n'
    response = firehose.put_record(DeliveryStreamName=firehose_delivery_stream, Record={'Data': record})
    return response
