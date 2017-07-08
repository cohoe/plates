import json
import boto3

def notifypending(event, context):
    """
    Send a notification of a pending review.
    """
    arn = "arn:aws:sns:us-east-1:460782256770:plates-PendingReviews"
    message = {"event": event}

    client = boto3.client('sns')

    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
