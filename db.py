import boto3
from flask import current_app
from datetime import datetime
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource(
    'dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
table = dynamodb.Table('Tasks')
GSI_name = "PriorityIndex"


def get_tasks():
    response = table.scan()
    print("getting tasks", response)
    items = response.get('Items', [])
    return items


def get_tasks_sorted_by_priority():
    # response = table.scan(IndexName=)
    response = table.query(
        IndexName=GSI_name,  # Use the GSI for the query
        KeyConditionExpression=Key('id').begins_with(''),
        ScanIndexForward=True  # Set to False for descending order
    )
    items = response.get('Items', [])
    return items


def get_task_by_id(task_id):
    response = table.query(KeyConditionExpression=Key('id').eq(task_id))
    items = response.get('Items', None)
    return items[0]


def get_max_priority():
    response = table.query(
        IndexName=GSI_name,
        ProjectionExpression='priority',
        ScanIndexForward=False,  # To get the highest priority first
        Limit=1  # We only need one result to get the maximum priority
    )

    items = response.get('Items', [{}])
    return items[0].get('priority', 0) + 1


def create_task(title, label):
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    priority = get_max_priority()
    table.put_item(Item={'id': task_id, 'title': title,
                   'label': label, 'created_at': created_at})
    return {'id': task_id, 'title': title, 'label': label, 'created_at': created_at, "priority": priority}


def edit_task(task_id, title, label):
    task = get_task_by_id(task_id)
    table.update_item(
        Key={'id': task_id, "created_at": task["created_at"]},
        UpdateExpression='SET title = :title, label = :label',
        ExpressionAttributeValues={':title': title, ':label': label},
        ReturnValues='ALL_NEW'
    )
    return {'id': task_id, 'title': title, 'label': label, "created_at": task["created_at"]}


def update_task_priority(task, priority):
    table.update_item(
        Key={'id': task["id"], "created_at": task["created_at"]},
        UpdateExpression='SET priority = :priority',
        ExpressionAttributeValues={':priority': priority},
        ReturnValues='ALL_NEW'
    )
    return {**task, "priority": priority}


def reorder_task(table, id, new_priority):
    task_item = get_task_by_id(id)

    if task_item:
        # Update order numbers to create a gap
        tasks_to_update = table.scan(
            IndexName=GSI_name,
            FilterExpression='priority > :priority',
            ExpressionAttributeValues={':priority': task_item['priority']}
        )['Items']

        for task in tasks_to_update:
            table.update_item(
                Key={'id': task['id']},
                UpdateExpression='SET #priority = :new_order',
                ExpressionAttributeNames={'#priority': 'priority'},
                ExpressionAttributeValues={':new_order': task['priority'] + 1},
            )

        # Move the task to the new order
        update_task_priority(task_item, new_priority)

        return True
    return False


def delete_task(task_id):
    task = get_task_by_id(task_id)
    response = table.delete_item(
        Key={'id': task_id, "created_at": task["created_at"]})
    return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200
