import json
import urllib.parse
import boto3
from uuid import uuid4

VENUES_TABLE_NAME="plates-venues"

def create(event, context):
    """
    Create a venue.
    """
    body = event['body']
    body_parsed = urllib.parse.parse_qs(body)

    required_keys = ['name', 'streetAddress', 'city', 'state']
    for key in required_keys:
        if key not in body_parsed.keys():
            message = "ERROR: Key \"%s\" not specified." % key
            response = {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": message
            }
            return response

    for key in body_parsed.keys():
        body_parsed[key] = body_parsed[key][0]

    if len(body_parsed['state']) != 2:
        message = "ERROR: State must be only two characters. Got \"%s\" (%i)." % (body_parsed['state'], len(body_parsed['state']))
        response = {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": message
        }
        return response

    message = ""
    for key in body_parsed.keys():
        message += "%s;" % key

    client = boto3.client('dynamodb')
    venue_id = str(uuid4())
    try:
        client.put_item(TableName=VENUES_TABLE_NAME,
                        Item={
                            'id': {'S': venue_id},
                            'name': {'S': body_parsed['name']},
                            'streetAddress': {'S': body_parsed['streetAddress']},
                            'city': {'S': body_parsed['city']},
                            'state': {'S': body_parsed['state']},
                        })

        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": "{\n\t\"SUCCESS\": \"%s\"\n}" % body_parsed['name']
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

def list(event, context):
    """
    List venues.
    """
    client = boto3.client('dynamodb')

    response = client.scan(TableName=VENUES_TABLE_NAME)

    venues = []
    for item in response['Items']:
        venue = {}
        for key in item.keys():
            # Theyre all strings so we can get away with this.
            venue[key] = item[key]["S"]
        venues.append(venue)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(venues)
    }
    return response
