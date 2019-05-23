import json
import logging
import boto3
import os


DEBUG = True                    # Set verbose debugging information

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)


def savePicToDynamodb(body, region='us-east-2'):
    
    userId = {'S' : body['userId']}
    pictureId = {'S' : body['pictureId']}
    caption = {'S' : ''}
    checked = {'S' : 'yup'}
    child = {'S' : ''}
    geopoint = {'S' : body['geopoint']}
    lat = {'S' : body['lat']}
    likes = {'N' : '0.0'}
    timestamp = {'N' : body['timestamp']}
    lng = {'S' : body['lng']}
    location = {'S' : body['location']}
    parent = {'S' : body['parent']}
    picMarker = {'S' : ''}
    picPath = {'S' : body['picPath']}
    username = {'S' : body['username']}
    bucket = body['bucket']
    photo = body['photo']
    hashtags = body['hashtags']
    tags = {}
    hashing = {}
    clientRek=boto3.client('rekognition')
    responseModeration = moderationLabels(bucket, photo, clientRek)
    responseLabels = labels(bucket, photo, clientRek)
    
    if(responseModeration):
        if('Nudity' in responseModeration[0]['Name']):
            checked = {'S' : 'Nudity'}
        if('Suggestive' in responseModeration[0]['Name']):
            checked = {'S' : 'Suggestive'}

    if(responseLabels):
        for labelss in responseLabels:
            label=labelss['Name'].replace(' ', '')
            label=label.lower()
            label='#'+label
            hashtags[label] = label
    # i=0
    for tag in hashtags:
        taggy = tag
        hashing[taggy]= {'S' : tag}
        # i+=1
        # hashtags[tag] = 
        
        
    tags = {'M':hashing}
    logger.info(tags)
    updateExpression='SET #checked = :checked, #geopoint = :geopoint, #lat = :lat, #likes = :likes, #lng = :lng, #location = :location, #parent = :parent, #picPath = :picPath, #username = :username, #hashtags = :hashtags, #timestamp = :timestamp'

    expressionAttributeNames={
        
        '#checked': 'checked',
        '#geopoint': 'geopoint',
        '#lat': 'lat',
        '#likes': 'likes',
        '#lng': 'lng',
        '#location': 'location',
        '#parent': 'parent',
        '#username': 'username',
        '#picPath': 'picPath',
        '#timestamp': 'timestamp',
        '#hashtags': 'hashtags'
    }
    expressionAttributeValues={
        
        ':checked': checked,
        ':geopoint': geopoint,
        ':lat': lat,
        ':likes': likes,
        ':picPath': picPath,
        ':lng': lng,
        ':location': location,
        ':parent': parent,
        ':username': username,
        ':timestamp': timestamp,
        ':hashtags': tags
    }

    if(body['caption']):
        caption = {'S' : body['caption']}
        
        updateExpression += ', #caption = :caption'
        expressionAttributeNames['#caption'] = 'caption'
        expressionAttributeValues[':caption'] = caption

    if('child' in body):
        child = {'S' : body['child']}
        updateExpression += ', #child = :child'
        expressionAttributeNames['#child'] = 'child'
        expressionAttributeValues[':child'] = child
        
    if('picMarker' in body):
        picMarker ={'S' : body['picMarker']}
        updateExpression += ', #picMarker = :picMarker'
        expressionAttributeNames['#picMarker'] = 'picMarker'
        expressionAttributeValues[':picMarker'] = picMarker
        
    
    clientDynamodb = boto3.client('dynamodb', 'us-east-2')
    
    response = clientDynamodb.update_item(
        TableName = 'comexamplebriannatur-mobilehub-577193899-pictures',
        Key={
            'userId': userId,
            'pictureId' : pictureId
        },
        UpdateExpression=updateExpression,
        ExpressionAttributeNames=expressionAttributeNames,
        ExpressionAttributeValues=expressionAttributeValues,
        ReturnValues='ALL_NEW'
    )
    logger.info(response)
    
    return json.dumps(response)
    
    
    
def labels(bucket, photo, client):
    
    responseLabels = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=20)
    logger.info(json.dumps(responseLabels['Labels']))    
            
    return responseLabels['Labels']

def moderationLabels(bucket, photo, client):
    
    responseModeration = client.detect_moderation_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
    logger.info(json.dumps(responseModeration['ModerationLabels'])) 
            
    return responseModeration['ModerationLabels']   
    

def handler(event, context):
    action = json.loads(event['body'])
    logger.error(json.dumps(action))
    body = savePicToDynamodb(action)
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = body
    return response
