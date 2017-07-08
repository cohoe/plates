import json
import boto3
import urllib.parse
from uuid import uuid4

PENDING_TABLE_NAME="plates-pendingreviews"

def submit(event, context):
    """
    Submit a review for moderation.
    """

    #message = json.dumps(event)
    
    body = event['body']
    body_parsed = urllib.parse.parse_qs(body)
    #message = body_parsed['fname']
    #message = body_parsed
    message = ""
    for key in body_parsed.keys():
        message += "%s;" % key

    message = body_parsed['fname'][0]

    client = boto3.client('dynamodb')
    review_id = str(uuid4())
    try:
        client.put_item(TableName=PENDING_TABLE_NAME,
                        Item={
                            'id': {'S': review_id},
                            'content': {'S': message}
                        })
        response = {
            "statusCode": 200,
            "body": "%s: OK" % review_id
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": "ERROR: %s" % e
        }

    return response

def approval(event, context):
    """
    Get a review for pending moderation.
    """
    #message = json.dumps(event)
    review_id = event['pathParameters']['review_id']

    client = boto3.client('dynamodb')
    try:
        query_response = client.get_item(TableName=PENDING_TABLE_NAME,
                                         Key={
                                             'id': {'S': review_id}
                                         })
        review = {'id': review_id, 'content': query_response['Item']['content']['S']}
        message = json.dumps(review)
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": message
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": "ERROR: %s" % e
        }

    return response

def reject(event, context):
    """
    Reject a pending review.
    """
    review_id = event['pathParameters']['review_id']

    client = boto3.client('dynamodb')
    try:
        client.delete_item(TableName=PENDING_TABLE_NAME,
                            Key={
                                'id': {'S': review_id}
                            })
        response = {
            "statusCode": 200,
            "body": "SUCCESS"
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": "ERROR: %s" % e
        }

    return response

def accept(event, context):
    """
    Accept a pending review.
    """
    review_id = event['pathParameters']['review_id']
    response = {
        "statusCode": 200,
        "body": "Not implemented yet."
    }

    return response
