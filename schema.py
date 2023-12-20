import graphene
import uuid
from datetime import datetime
import db
from flask_graphql import GraphQLView


class Task(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    label = graphene.String()
    created_at = graphene.String()


class Query(graphene.ObjectType):
    tasks = graphene.List(Task)
    labels = graphene.List(graphene.String)

    def resolve_tasks(self, info):
        items = db.get_tasks()
        return [Task(id=item['id'], title=item['title'], label=item['label'], created_at=item['created_at']) for item in items]

    def resolve_labels(self, info):
        items = db.get_tasks()
        return ["to-do", "in-progress", "review", "done"]


class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        label = graphene.String()

    task = graphene.Field(Task)

    def mutate(self, info, title, label):
        task_data = db.create_task(title, label)
        return CreateTask(task=Task(**task_data))


class EditTask(graphene.Mutation):
    class Arguments:
        taskId = graphene.String()
        title = graphene.String()
        label = graphene.String()
        created_at = graphene.String()

    task = graphene.Field(Task)

    def mutate(self, info, taskId, title, label):
        task = db.edit_task(taskId, title, label)
        return EditTask(task=Task(**task))


class DeleteTask(graphene.Mutation):
    class Arguments:
        taskId = graphene.String()

    success = graphene.Boolean()

    def mutate(self, info, taskId):
        success = db.delete_task(taskId)
        return DeleteTask(success=success)


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    edit_task = EditTask.Field()
    delete_task = DeleteTask.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
graphql_view = GraphQLView.as_view('graphql', schema=schema, graphiql=True)
