import json
import boto3

def notifypending(event, context):
    """
    Send a notification of a pending review.
    """
    arn = "arn:aws:sns:us-east-1:460782256770:plates-PendingReviews"
    url_prefix="http://platesofrochester.s3-website-us-east-1.amazonaws.com/approval.html?id="

    #message = {"event": event}

    operation = event['Records'][0]['eventName']

    if "INSERT" not in operation:
        return

    review_id = event['Records'][0]['dynamodb']['Keys']['id']['S']
    message = "Review %s%s has been submitted for review." % (url_prefix, review_id)

    client = boto3.client('sns')

    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': message}),
        MessageStructure='json'
    )
