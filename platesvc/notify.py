#!/usr/bin/env python3

import json
import boto3

arn = "arn:aws:sns:us-east-1:460782256770:plates-PendingReviews"
message = {"foo": "bar"}
client = boto3.client('sns')

response = client.publish(
    TargetArn=arn,
#    Message=json.dumps({'default': json.dumps(message)}),
    Message=json.dumps({'default': "The quick brown fox is a <a href=\"http://google.com\">snarky ass-munch</a>."}),
    MessageStructure='json'
)
