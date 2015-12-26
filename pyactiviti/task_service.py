from pyactiviti.base import (
    Service,
    Query,
    JavaDictMapper,
    NotFound,
)
import pdb
import iso8601


class Task:

    def __init__(self, id):
        self.id = id

    def parse(self, dict_task):
        JavaDictMapper.update_object(self, dict_task)
        self.create_time = iso8601.parse_date(self.create_time)
        self.due_date = iso8601.parse_date(self.due_date)
        self.execution = Task._get_id(self.execution)
        if self.parent_task:
            self.parent_task = Task._get_id(self.parent_task)
        if self.process_instance:
            self.process_instance = Task._get_id(self.process_instance)

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

    def __init__(self, engine):
        url_path = "/query/tasks"
        Query.__init__(self, engine, url_path)

    def name(self, value):
        self._add_parameter_with_like("name", value)
        return self

    def description(self, value):
        self._add_parameter("description", value)
        return self

    def priority(self, value, operator="equals"):
        parameters = {"equals": "priority", "less": "maximumPriority",
                    "greater": "minimumPriority"}
        if operator in parameters:
            self._add_parameter(parameters[operator], value)
        return self

    def assignee(self, value):
        if value:
            self._add_parameter_with_like("assignee", value)
        else:
            self.parameters["unassigned"] = True
        return self

    def owner(self, value):
        self._add_parameter_with_like("owner", value)
        return self

    def delegation_state(self, value):
        if value in ("pending", "resolved"):
            self._add_parameter("delegationState", value)
        return self

    def candidate_user(self, value):
        self._add_parameter("candidateUser", value)
        return self

    def candidate_group(self, *args):
        if len(args) == 1:
            self.parameters["candidateGroup"] = args[0]
        else:
            self.parameters["candidateGroups"] = ", ".join(args)
        return self

    def involved_user(self, value):
        self._add_parameter("involvedUser", value)
        return self

    def task_definition_key(self, value):
        self._add_parameter_with_like("taskDefinitionKey", value)
        return self

    def process_instance(self, obj):
        self._add_parameter_object("processInstanceId", obj)
        return self

    def process_instance_business_key(self, value):
        self._add_parameter_with_like("processInstanceBusinessKey", value)
        return self

    def process_definition_key(self, value):
        self._add_parameter_with_like("processDefinitionKey", value)
        return self

    def process_definition_name(self, value):
        self._add_parameter_with_like("processDefinitionName", value)
        return self

    def execution(self, obj):
        self._add_parameter_object("executionId", obj)
        return self

    def created_date(self, value, operator="on"):
        parameters = {"on": "createdOn", "before": "createdBefore",
                                "after": "createdAfter"}
        if operator in parameters:
            str_date = value.isoformat()
            self._add_parameter(parameters[operator], str_date)
        return self

    def due_date(self, value, operator="on"):
        if value:
            parameters = {"on": "dueOn", "before": "dueBefore",
                                    "after": "dueAfter"}
            if operator in parameters:
                str_date = value.isoformat()
                self._add_parameter(parameters[operator], str_date)
        else:
            self._add_parameter("withoutDueDate", True)
        return self

    def exclude_subtasks(self):
        self._add_parameter("excludeSubTasks", True)
        return self

    def active(self):
        self._add_parameter("active", True)
        return self

    def include_task_local_variables(self):
        self._add_parameter("includeTaskLocalVariables", True)
        return self

    def include_process_variables(self):
        self._add_parameter("includeProcessVariables", True)
        return self

    def tenant_id(self, value):
        if value:
            self._add_parameter_with_like("tenantId", value)
        else:
            self._add_parameter("withoutTenantId", True)
        return self

    def candidate_or_assigned(self, value):
        self._add_parameter("candidateOrAssigned", value)
        return self
