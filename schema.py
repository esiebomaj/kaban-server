import graphene
import uuid
from datetime import datetime
import db
from flask_graphql import GraphQLView


class Task(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    label = graphene.String()
    priority = graphene.Int()
    created_at = graphene.String()
    board_id = graphene.String()


class Query(graphene.ObjectType):
    tasks = graphene.List(Task, board_id=graphene.String(),
                          sort_by=graphene.String())
    labels = graphene.List(graphene.String)

    def resolve_tasks(self, info, board_id, sort_by="priority"):
        if sort_by == "priority":
            items = db.get_tasks_sorted_by_priority(board_id)
        else:
            items = db.get_tasks(board_id)

        return [Task(**item) for item in items]

    def resolve_labels(self, info):
        return ["to-do", "in-progress", "review", "done"]


class CreateTask(graphene.Mutation):
    class Arguments:
        board_id = graphene.String()
        title = graphene.String()
        label = graphene.String()

    task = graphene.Field(Task)

    def mutate(self, info, board_id, title, label):
        task_data = db.create_task(board_id, title, label)
        return CreateTask(task=Task(**task_data))


class EditTask(graphene.Mutation):
    class Arguments:
        board_id = graphene.String()
        task_id = graphene.String()
        title = graphene.String()
        label = graphene.String()
        created_at = graphene.String()

    task = graphene.Field(Task)

    def mutate(self, info, board_id, task_id, title, label):
        task = db.edit_task(board_id, task_id, title, label)
        return EditTask(task=Task(**task))


class DeleteTask(graphene.Mutation):
    class Arguments:
        boardId = graphene.String()
        taskId = graphene.String()

    success = graphene.Boolean()

    def mutate(self, info, boardId, taskId):
        success = db.delete_task(boardId, taskId)
        return DeleteTask(success=success)


class ReorderTask(graphene.Mutation):
    class Arguments:
        board_id = graphene.String()
        task_id = graphene.String()
        priority = graphene.Int()

    success = graphene.Boolean()

    def mutate(self, info, board_id, task_id, priority):
        success = db.reorder_task(board_id, task_id, priority)
        return ReorderTask(success=success)


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    edit_task = EditTask.Field()
    delete_task = DeleteTask.Field()
    reorder_task = ReorderTask.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
graphql_view = GraphQLView.as_view('graphql', schema=schema, graphiql=True)
