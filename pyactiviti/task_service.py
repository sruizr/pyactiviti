from pyactiviti.base import (
                             Service,
                             Query,
                             JavaDictMapper,
                             NotFound,
                             )
import iso8601


class Task:
    def __init__(self, id):
        self.id = id

    def parse(self, dict_task):
        a = iso8601.
        JavaDictMapper.update_object(self, dict_task)
        self.create_time = iso       convert(self.create_time)
        self.due_date = Task._convert_to_time(self.due_date)
        self.execution = Task._get_id(self.execution)
        if self.parent_task:
            self.parent_task = Task._get_id(self.parent_task)
        if self.process_instance:
            self.process_instance = Task._get_id(self.process_instance)
            Task.

    @staticmethod
    def _get_id(url):
        tokens = url.split("/")
        return tokens[-1]


class TaskService(Service):

    def __init__(self, engine):
        Service.__init__(self, engine, "runtime")

    def load_task(self, task):
        try:
            dict_task = self.load("tasks", task.id)
            task.parse(dict_task)
        except NotFound:
            raise TaskNotFound()


class TaskNotFound(NotFound):
    pass


class TaskQuery(Query):
    def __init__(self, service):
        Query.__init__(self, service)

    def name(self, value):
        self._add_parameter_with_like("name", value)

    def description(self, value):

        self._add_parameter("description", value)

    def priority(self, operator, value):

        self._add_parameter("priority", value)

    def assignee(self, value):
        if value:
            self._add_parameter_with_like("assignee", value)
        else:
            self.parameters["unassigned"] = True

    def owner(self, value):
        self._add_parameter_with_like("owner", value)

    def delegation_state(self, value):
        if value in ("pending", "resolved"):
            self._add_parameter("delegationState", value)

    def candidate_user(self, value):
        self._add_parameter("candidateUser", value)

