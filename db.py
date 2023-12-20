import boto3
from flask import current_app
from datetime import datetime
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
table = dynamodb.Table('Tasks')


def get_tasks():
    response = table.scan()
    items = response.get('Items', [])
    return items

def get_task_by_id(task_id):
    response = table.query(KeyConditionExpression=Key('id').eq(task_id))
    items = response.get('Items', None)
    return items[0]


def create_task(title, label):
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    table.put_item(Item={'id': task_id, 'title': title, 'label': label, 'created_at': created_at})
    return {'id': task_id, 'title': title, 'label': label, 'created_at': created_at}


def edit_task(task_id, title, label):
    task = get_task_by_id(task_id)
    table.update_item(
        Key={'id': task_id, "created_at": task["created_at"]},
        UpdateExpression='SET title = :title, label = :label',
        ExpressionAttributeValues={':title': title, ':label': label},
        ReturnValues='ALL_NEW'
    )
    return {'id': task_id, 'title': title, 'label': label, "created_at": task["created_at"]}


def delete_task(task_id):
    task = get_task_by_id(task_id)
    response = table.delete_item(Key={'id': task_id, "created_at": task["created_at"]})
    return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200
