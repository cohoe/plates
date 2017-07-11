import json
import boto3
import urllib.parse
from uuid import uuid4
from datetime import datetime

PENDING_TABLE_NAME="plates-pendingreviews"
PUBLISHED_TABLE_NAME="plates-publishedreviews"

def submit(event, context):
    """
    Submit a review for moderation.
    """

    #message = json.dumps(event)
    
    body = event['body']
    body_parsed = urllib.parse.parse_qs(body)

    # The parse_qs function converts all values to a list, even if there is only one.
    for key in body_parsed.keys():
        body_parsed[key] = body_parsed[key][0]

    required_keys = ["reviewer", "sketchiness", "serviceQuality", "responseTime", "value", "presentation", "primaryBaseRating", "meatRating"]
    allowed_keys = ['reviewer', 'firstplate', 'venue', 'venuecomments', 'sketchiness', 'partysize', 'serviceQuality', 'responseTime', 'value', 'presentation', 'portionSize', 'primaryBaseRating', 'primaryBaseComment', 'secondaryBaseRating', 'secondaryBaseComment', 'primaryBase', 'meatRating', 'meatComments', 'sauce', 'sauceRating', 'sauceComments', 'bread', 'miscComments']

    bool_keys = ['firstplate', 'sauce', 'bread']
    number_keys = ['partysize', 'sketchiness', 'serviceQuality', 'responseTime', 'value', 'presentation', 'portionSize', 'primaryBaseRating', 'secondaryBaseRating', 'meatRating', 'sauceRating']
    # Venue Validate

    # Test that all minimum required keys are present
    for key in required_keys:
        if key not in body_parsed.keys():
            message = "ERROR: Key \"%s\" not specified." % key
            response = {
                "statusCode": 400,
                "headers": {
                    "access-control-allow-origin": "*"
                },
                "body": "{\n\tERROR: %s\n}" % message
            }
            return response

    # Test that all keys given are actually valid.
    for key in body_parsed.keys():
        if key not in allowed_keys:
            message = "ERROR: Key \"%s\" was specified but is not allowed." % key
            response = {
                "statusCode": 400,
                "headers": {
                    "access-control-allow-origin": "*"
                },
                "body": "{\n\tERROR: %s\n}" % message
            }
            return response

    # Build an item based on AWS data types
    item = {}
    for key in body_parsed.keys():
        if key in bool_keys:
            item[key] = {"BOOL": bool(body_parsed[key])}
        elif key in number_keys:
            item[key] = {"N": body_parsed[key]}
        else:
            item[key] = {"S": body_parsed[key]}

    # Assign it an ID and stash a date
    review_id = str(uuid4())
    item['id'] = {"S": review_id}
    item['date'] = {"S": str(datetime.utcnow())}

    # Stick it in. What could go wrong...
    client = boto3.client('dynamodb')
    try:
        client.put_item(TableName=PENDING_TABLE_NAME,
                        Item=item)
        response = {
            "statusCode": 200,
            "headers": {
                "access-control-allow-origin": "*"
            },
            "body": "{\n\t\"ok\": \"%s\"\n}" % review_id
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
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
        #review = {'id': review_id, 'content': query_response['Item']['content']['S']}
        review = query_response['Item']

        clean_review = {}
        for key in review.keys():
            d_type = list(review[key].keys())[0]
            clean_review[key] = review[key][d_type]

        message = json.dumps(clean_review)
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
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
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
    try:
        client = boto3.client('dynamodb')
        query_response = client.get_item(TableName=PENDING_TABLE_NAME,
                                         Key={
                                             'id': {'S': review_id}
                                         })
        pending_review = query_response['Item']
        pending_review['pub_date'] = {'S': str(datetime.utcnow())}

        pub_response = client.put_item(TableName=PUBLISHED_TABLE_NAME,
                                       Item=pending_review)

    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": "ERROR: %s" % e
        }
        return response

    response = {
        "statusCode": 200,
        "body": "{}"
    }

    return response

def get(event, context):
    """
    Get a particular review.
    """
    review_id = event['pathParameters']['review_id']

    try:
        client = boto3.client('dynamodb')
        query_response = client.query(TableName=PUBLISHED_TABLE_NAME,
                                        IndexName="ReviewsByIdIndex",
                                        KeyConditionExpression='id = :review_id',
                                        ExpressionAttributeValues={
                                            ':review_id': {'S': review_id}
                                        })

        review = query_response['Items'][0]

        clean_review = {}
        for key in review.keys():
            d_type = list(review[key].keys())[0]
            clean_review[key] = review[key][d_type]

        message = json.dumps(clean_review)
        #message = json.dumps(query_response)
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
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": "ERROR: %s" % e
        }
        return response

    return response

def listrevs(event, context):
    """
    List reviews.
    """
    client = boto3.client('dynamodb')

    response = client.scan(TableName=PUBLISHED_TABLE_NAME)

    reviews = []
    for item in response['Items']:
        review = {}
        for key in item.keys():
            d_type = list(item[key].keys())[0]
            review[key] = item[key][d_type]
        reviews.append(review)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(reviews)
    }
    return response

def listvenuerevs(event, context):
    """
    List reviews for a venue.
    """
    venue_id = event['pathParameters']['venue_id']

    try:
        client = boto3.client('dynamodb')
        query_response = client.query(TableName=PUBLISHED_TABLE_NAME,
                                        KeyConditionExpression='venue = :venue_id',
                                        ExpressionAttributeValues={
                                            ':venue_id': {'S': venue_id}
                                        })

        reviews = query_response['Items']

        clean_reviews = []

        for review in reviews:
            clean_review = {}
            for key in review.keys():
                d_type = list(review[key].keys())[0]
                clean_review[key] = review[key][d_type]
            clean_reviews.append(clean_review)

        message = json.dumps(clean_reviews)
        #message = json.dumps(query_response)
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
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": "ERROR: %s" % e
        }
        return response

    return response
