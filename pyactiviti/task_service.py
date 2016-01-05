from pyactiviti.base import (
    Service,
    Query,
    JavaDictMapper,
    NotFound,
    Variables,
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
            self.task_variables = Variables(self.task_variables)
        if hasattr(self, "process_variables"):
            self.process_variables = Variables(self.process_variables)

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

    def complete(self, task):
        variables = task.process_variables.sync_rest()
        variables += task.task_variables.sync_rest()
        dict_post = {"action": "complete", "variables": variables}
        self.post_with_json(dict_post, "tasks", task.id)

    def add_comment(self, task, message):
        dict_message = {"message": message, "saveProcessInstanceId": True}
        self.post_with_json(dict_message, "tasks", task.id, "comments")


class TaskNotFound(NotFound):
    pass


class TaskQuery(Query):

    def __init__(self, engine):
        url_path = "/query/tasks"
        Query.__init__(self, engine, url_path)

    def name(self, value):
        self._add_filter_with_like("name", value)
        return self

    def description(self, value):
        self._add_filter("description", value)
        return self

    def priority(self, operator, value):
        self._add_filter_("priority", value)

    def priority(self, value, operator="equals"):
        filters = {"equals": "priority", "less": "maximumPriority",
                    "greater": "minimumPriority"}
        if operator in filters:
            self._add_filter(filters[operator], value)
        return self

    def assignee(self, value):
        if value:
            self._add_filter_with_like("assignee", value)
        else:
            self.filters["unassigned"] = True
        return self

    def owner(self, value):
        self._add_filter_with_like("owner", value)
        return self

    def delegation_state(self, value):
        if value in ("pending", "resolved"):
            self._add_filter("delegationState", value)
        return self

    def candidate_user(self, value):
        self._add_filter("candidateUser", value)
        return self

    def candidate_group(self, *args):
        if len(args) == 1:
            self.filters["candidateGroup"] = args[0]
        else:
            self.filters["candidateGroups"] = ", ".join(args)
        return self

    def involved_user(self, value):
        self._add_filter("involvedUser", value)
        return self

    def task_definition_key(self, value):
        self._add_filter_with_like("taskDefinitionKey", value)
        return self

    def process_instance(self, obj):
        self._add_filter_object("processInstanceId", obj)
        return self

    def process_instance_business_key(self, value):

        self._add_filter_with_like("processInstanceBusinessKey", value)
        return self

    def process_definition_key(self, value):
        self._add_filter_with_like("processDefinitionKey", value)
        return self

    def process_definition_name(self, value):
        self._add_filter_with_like("processDefinitionName", value)
        return self

    def execution(self, obj):
        self._add_filter_object("executionId", obj)
        return self

    def created_date(self, value, operator="on"):
        filters = {"on": "createdOn", "before": "createdBefore",
                                "after": "createdAfter"}
        if operator in filters:
            str_date = value.isoformat()
            self._add_filter(filters[operator], str_date)
        return self

    def due_date(self, value, operator="on"):
        if value:
            filters = {"on": "dueOn", "before": "dueBefore",
                                    "after": "dueAfter"}
            if operator in filters:
                str_date = value.isoformat()
                self._add_filter(filters[operator], str_date)
        else:
            self._add_filter("withoutDueDate", True)
        return self

    def exclude_subtasks(self):
        self._add_filter("excludeSubTasks", True)
        return self

    def active(self):
        self._add_filter("active", True)
        return self

    def include_task_local_variables(self):
        self._add_filter("includeTaskLocalVariables", True)
        return self

    def include_process_variables(self):
        self._add_filter("includeProcessVariables", True)
        return self

    def tenant_id(self, value):
        if value:
            self._add_filter_with_like("tenantId", value)
        else:
            self._add_filter("withoutTenantId", True)
        return self

    def candidate_or_assigned(self, value):
        self._add_filter("candidateOrAssigned", value)
        return self

    def list(self):
        data_request = self.filters.copy()
        if self.variable_filter:
            data_request["processInstanceVariables"] = self.variable_filter

        values = json.dumps(data_request)
        json_response = self.list_post()

        json_task_list = json_response["data"]
        task_list = []

        for item in json_task_list:
            task_list.append(Task(item))

        return task_list
