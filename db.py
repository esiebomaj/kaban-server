import boto3
from flask import current_app
from datetime import datetime
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource(
    'dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
table = dynamodb.Table('Tasks')
PRIORITY_GSI = "PriorityIndex"
CREATED_AT_GSI = "CreatedAtIndex"


def get_tasks(board_id):
    response = table.query(
        IndexName=CREATED_AT_GSI,
        KeyConditionExpression=Key('board_id').eq(board_id),
        ScanIndexForward=False
    )
    items = response.get('Items', [])
    return items


def get_tasks_sorted_by_priority(board_id):
    response = table.query(
        IndexName=PRIORITY_GSI,
        KeyConditionExpression=Key('board_id').eq(board_id),
        ScanIndexForward=False
    )
    items = response.get('Items', [])
    return items


def get_task_by_id(board_id, task_id):
    response = table.get_item(
        Key={
            'board_id': board_id,
            'id': task_id
        }
    )
    task = response.get('Item')
    return task


def get_max_priority(board_id):
    response = table.query(
        IndexName=PRIORITY_GSI,
        KeyConditionExpression=Key('board_id').eq(board_id),
        ProjectionExpression='priority',
        ScanIndexForward=False,  # To get the highest priority first
        Limit=1
    )
    items = response.get('Items', [{}])
    return items[0].get('priority', 0) + 1 if len(items) > 0 else 0


def create_task(board_id, title, label):
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    priority = get_max_priority(board_id)
    table.put_item(Item={'id': task_id, "board_id": board_id, 'title': title, 'label': label,
                   'created_at': created_at, "priority": priority})
    return {"board_id": board_id, 'id': task_id, 'title': title, 'label': label, 'created_at': created_at, "priority": priority}


def edit_task(board_id, task_id, title, label):
    res = table.update_item(
        Key={'id': task_id, "board_id": board_id},
        UpdateExpression='SET title = :title, label = :label',
        ExpressionAttributeValues={':title': title, ':label': label},
        ReturnValues='ALL_NEW'
    )
    item = res.get("Attributes", {})
    return item


def update_task_priority(task, priority):
    table.update_item(
        Key={'id': task["id"], "board_id": task["board_id"]},
        UpdateExpression='SET priority = :priority',
        ExpressionAttributeValues={':priority': priority},
        ReturnValues='ALL_NEW'
    )
    return {**task, "priority": priority}


def reorder_task(board_id, id, new_priority):
    curr_task = get_task_by_id(board_id, id)
    old_priority = curr_task["priority"]

    if curr_task:
        if new_priority < old_priority:
            key_condition = Key('board_id').eq(board_id) & Key(
                'priority').between(new_priority, old_priority)
        else:
            key_condition = Key('board_id').eq(board_id) & Key(
                'priority').between(old_priority, new_priority)

        # Update order numbers to create a gap
        tasks_to_update = table.query(
            IndexName=PRIORITY_GSI,
            KeyConditionExpression=key_condition
        )['Items']

        # this is somewhat inefficient but we can assume that we have a limit of tasks on each board
        for task in tasks_to_update:
            if new_priority < old_priority:
                update_task_priority(task, task['priority'] + 1)
            else:
                update_task_priority(task, task['priority'] - 1)

        # Move the task to the new order
        update_task_priority(curr_task, new_priority)

        return True
    return False


def delete_task(board_id, task_id):
    response = table.delete_item(
        Key={'id': task_id, "board_id": board_id})
    return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200
