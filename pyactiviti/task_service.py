from pyactiviti.base import (
    Service,
    Query,
    JavaDictMapper,
    NotFound,
)
import json
import pdb
import iso8601


class Task:
    def __init__(self, camel_case_data=None):
        if camel_case_data:
            self._parse(camel_case_data)

    def _parse(self, camel_case_data):
        JavaDictMapper.update_object(self, camel_case_data)
        if hasattr(self, "create_time"):
            self.create_time = iso8601.parse_date(self.create_time)
        if hasattr(self, "due_date"):
            self.due_date = iso8601.parse_date(self.due_date)
        self.execution = self._get_id(self.execution)
        if hasattr(self, "parent_task"):
            self.parent_task = self._get_id(self.parent_task)
        if hasattr(self, "process_instance"):
            self.process_instance = self._get_id(self.process_instance)
        if hasattr(self, "task_variables"):
            pass
        if hasattr(self, "process_variables"):
            pass

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
            task = Task(dict_task)
        except NotFound:
            raise TaskNotFound()

    def claim(self, task, user):
        dict_post = {"action": "claim", "assignee": user.id}
        self.post_with_json(dict_post, "tasks", task.id)


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

    def priority(self, operator, value):
        self._add_parameter("priority", value)

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

    def list(self):
        data_request = self.parameters.copy()
        if self.variable_parameter:
            data_request["processInstanceVariables"] = self.variable_parameter
        values = json.dumps(data_request)
        json_response = self.session.post(self.url, data=values).json()
        json_task_list = json_response["data"]
        task_list = []
        for dict_task in json_task_list:
            task_list.append("fff")

        return task
