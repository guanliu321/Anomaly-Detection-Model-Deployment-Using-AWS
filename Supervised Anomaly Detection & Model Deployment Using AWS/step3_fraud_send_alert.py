#from __future__ import print_function
import boto3
import base64
import json

client = boto3.client('sns')
# Include your SNS topic ARN here.
topic_arn = 'arn:aws:sns:us-east-1:385078523302:fraud-alert'


def lambda_handler(event, context):
    output = []
    success = 0
    failure = 0
    for record in event['records']:
        try:


            # Uncomment the below line to publish the decoded data to the SNS topic.
            payload = str(base64.b64decode(record['data']),'utf-8')
            payload = json.loads(payload)
            #print("raw data in json: {}".format(payload))
            #print(type(payload['TIME_VALUE']))

            msg = 'An anomaly is detected on the portal at {}, with record id {}'.format(payload['TIME_VALUE'],payload['ID'])
            #print(msg)

            client.publish(TopicArn=topic_arn, Message=msg, Subject='Alert: an Anomal behavior is detected')
            output.append({'recordId': record['recordId'], 'result': 'Ok'})
            success += 1
        except Exception as e:
            print(e)
            output.append({'recordId': record['recordId'], 'result': 'DeliveryFailed'})
            failure += 1

    print('Successfully delivered {0} records, failed to deliver {1} records'.format(success, failure))
    return {'records': output}
