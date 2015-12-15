from .base import Service


class Task:

    def __init__(self):

        self.assignee = None
        self.execution = None
        self.id = None
        self.priority = None
        self.process_instance = None
        self.task_definition_key = None
        self.comments = None
        self.__sync__ = self.__dict__


class Comment:

    def __init__(self):
        self.task = None
        self.full_message = None
        self.id = None
        self.user = None


class TaskService(Service):

    def complete(self, task, user):
        pass
