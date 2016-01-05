import json
import pyactiviti.task_service as ts
from pyactiviti.process_engine import ActivitiEngine
import pyactiviti.base as b
from unittest.mock import Mock, patch
from .base import TestQuery
import pdb
import pytest
import iso8601
import datetime


class A_Task:

    def should_parse_from_dict(self):
        json_task = """{
  "assignee" : "kermit",
  "createTime" : "2013-04-17T10:17:43.902+0000",
  "delegationState" : "pending",
  "description" : "Task description",
  "dueDate" : "2013-04-17T10:17:43.902+0000",
  "execution" : "http://localhost:8182/runtime/executions/5",
  "id" : "8",
  "name" : "My task",
  "owner" : "owner",
  "parentTask" : "http://localhost:8182/runtime/tasks/9",
  "priority" : 50,
  "processDefinition" : "http://localhost:8182/repository/process-definitions/oneTaskProcess%3A1%3A4",
  "processInstance" : "http://localhost:8182/runtime/process-instances/5",
  "suspended" : false,
  "taskDefinitionKey" : "theTask",
  "url" : "http://localhost:8182/runtime/tasks/8",
  "tenantId" : null,
  "taskVariables": [
        {
          "name": "test",
          "scope": "local",
          "value": 99.9
        }
      ],
    "processVariables": [
        {
          "name": "processTest",
          "scope": "global",
          "value": "myProcessTest"
        }
      ]
}"""
        dict_task = json.loads(json_task)
        ref_time = iso8601.parse_date("2013-04-17T10:17:43.902+0000")

        task = ts.Task(dict_task)
        assert task.assignee == "kermit"
        assert task.create_time == ref_time
        assert task.due_date == ref_time
        assert task.delegation_state == "pending"
        assert task.description == "Task description"
        assert task.execution == "5"
        assert task.id == "8"
        assert task.name == "My task"
        assert task.owner == "owner"
        assert task.parent_task == "9"
        assert task.priority == 50
        assert task.process_instance == "5"
        assert not task.suspended
        assert not task.tenant_id
        assert len(task.process_variables) == 1
        assert task.process_variables["processTest"] == "myProcessTest"
        assert task.task_variables["test_"] == 99.9


class A_TaskService:

    def setup_method(self, method):
        engine = ActivitiEngine("http://localhost:8080")
        self.task_service = ts.TaskService(engine)

    def get_dict_task(self):
        json_task = """{
  "assignee" : "kermit",
  "createTime" : "2013-04-17T10:17:43.902+0000",
  "delegationState" : "pending",
  "description" : "Task description",
  "dueDate" : "2013-04-17T10:17:43.902+0000",
  "execution" : "http://localhost:8182/runtime/executions/5",
  "id" : "8",
  "name" : "My task",
  "owner" : "owner",
  "parentTask" : "http://localhost:8182/runtime/tasks/9",
  "priority" : 50,
  "processDefinition" : "http://localhost:8182/repository/process-definitions/oneTaskProcess%3A1%3A4",
  "processInstance" : "http://localhost:8182/runtime/process-instances/5",
  "suspended" : false,
  "taskDefinitionKey" : "theTask",
  "url" : "http://localhost:8182/runtime/tasks/8",
  "tenantId" : null,
  "taskVariables": [
        {
          "name": "test",
          "scope": "local",
          "value": "myTest"
        }
      ],
    "processVariables": [
        {
          "name": "processTest",
          "scope": "global",
          "value": "myProcessTest"
        }
      ]
}"""
        return json.loads(json_task)

    def get_task(self):
        task = ts.Task(self.get_dict_task())

        return task

    def should_has_correct_url_base(self):
        assert self.task_service.url == "http://localhost:8080/runtime"

    @patch("pyactiviti.task_service.Service.load")
    def should_load_task(self, mock_load):
        mock_load.return_value = self.get_dict_task()

        task = self.get_task()
        self.task_service.load_task(task)

        expected_task = self.get_task()
        assert task.description == expected_task.description
        assert task.id == expected_task.id

    @patch("pyactiviti.task_service.Service.load")
    def should_raise_exception_when_loading_unexisting_task(self, mock_load):
        mock_load.side_effect = b.NotFound()

        task = ts.Task()
        task.id = "10"
        with pytest.raises(ts.TaskNotFound):
            self.task_service.load_task(task)

    def should_supply_task_query(self):
        pass

    @patch("pyactiviti.task_service.Service.post_with_json")
    def should_claim_a_task(self, mock_post):
        mock_user = Mock()
        mock_user.id = "userId"
        task = self.get_task()
        self.task_service.claim(task, mock_user)

        dict_post = {"action": "claim", "assignee": "userId"}
        mock_post.assert_called_with(dict_post, "tasks", task.id)

    @patch("pyactiviti.task_service.Service.post_with_json")
    def should_complete_a_task(self, mock_post):

        task = self.get_task()
        task.process_variables["newVariableTest"] = 1234
        task.task_variables["otherVar_"] = 567
        self.task_service.complete(task)

        dict_post = {"action": "complete", "variables": [{
                                "name": "newVariableTest",
                                "value": 1234, "scope": "global"
                                },
                                {
                                "name": "otherVar",
                                "value": 567,
                                "scope": "local"
                                }]}
        mock_post.assert_called_with(dict_post, "tasks", task.id)

    @patch("pyactiviti.task_service.Service.post_with_json")
    def should_add_comment(self, mock_post):
        task = Mock()
        task.id = "8"
        dict_comment = {"message": "This is a comment on the task.",
                                        "saveProcessInstanceId": True}

        self.task_service.add_comment(task, "This is a comment on the task.")
        mock_post.assert_called_with(dict_comment, "tasks", task.id,
                                     "comments")

    def it_should_add_attachment_to_task(self, mock_post):
        pass


class A_TaskQuery(TestQuery):

    def setup_method(self, method):
        engine = ActivitiEngine("http://localhost:8080/rest_engine")
        self.query = ts.TaskQuery(engine)
        self.json_task_list = """{
  "data": [
    {
      "assignee" : "kermit",
      "createTime" : "2013-04-17T10:17:43.902+0000",
      "delegationState" : "pending",
      "description" : "Task description",
      "dueDate" : "2013-04-17T10:17:43.902+0000",
      "execution" : "http://localhost:8182/runtime/executions/5",
      "id" : "8",
      "name" : "My task",
      "owner" : "owner",
      "parentTask" : "http://localhost:8182/runtime/tasks/9",
      "priority" : 50,
      "processDefinition" : "http://localhost:8182/repository/process-definitions/oneTaskProcess%3A1%3A4",
      "processInstance" : "http://localhost:8182/runtime/process-instances/5",
      "suspended" : false,
      "taskDefinitionKey" : "theTask",
      "url" : "http://localhost:8182/runtime/tasks/8",
      "tenantId" : null
    },
        {
      "assignee" : "fozzy",
      "createTime" : "2013-04-17T10:17:43.902+0000",
      "delegationState" : "pending",
      "description" : "Task description",
      "dueDate" : "2013-04-17T10:17:43.902+0000",
      "execution" : "http://localhost:8182/runtime/executions/5",
      "id" : "9",
      "name" : "My task",
      "owner" : "owner",
      "parentTask" : "http://localhost:8182/runtime/tasks/9",
      "priority" : 100,
      "processDefinition" : "http://localhost:8182/repository/process-definitions/oneTaskProcess%3A1%3A4",
      "processInstance" : "http://localhost:8182/runtime/process-instances/6",
      "suspended" : true,
      "taskDefinitionKey" : "theTask",
      "url" : "http://localhost:8182/runtime/tasks/9",
      "tenantId" : null,
      "processVariables": null
    }

  ],
  "total": 2,
  "start": 0,
  "sort": "name",
  "order": "asc",
  "size": 2
}"""
        self.json_task_list = json.loads(self.json_task_list)

    def should_be_initialized_with_service(self):
        assert not self.query.filters
        assert self.query.url == "http://localhost:8080/rest_engine/query/tasks"

    def should_add_parameters_to_task(self):
        fake_object = Mock()
        fake_object.id = "objectId"
        query = self.query

        self.test_parameter_with_like(query.name, "name", "a name")
        self.test_parameter(query.description, "description",
                            "task description")
        self.test_parameter_numerical(query.priority, "minimumPriority",
                                      "greater", 12)
        self.test_parameter(query.priority, "priority", 10)
        self.test_parameter_numerical(query.priority, "maximumPriority",
                                      "less", 10)
        self.test_parameter_with_like(query.assignee, "assignee", "sRuiz")

        q = query.assignee(None)
        assert q.filters["unassigned"] == True
        q.filters.pop("unassigned")

        self.test_parameter_with_like(query.owner, "owner", "sRuiz")
        self.test_parameter(query.delegation_state, "delegationState",
                            "pending")
        self.test_parameter(query.delegation_state, "delegationState",
                            "resolved")
        q = query.delegation_state("nostate")
        assert "unassigned" not in q.filters

        self.test_parameter(query.candidate_user, "candidateUser",
                            "sRuiz")
        self.test_parameter(query.candidate_group, "candidateGroup",
                            "testGroup")
        q = query.candidate_group("group1", "group2")
        assert q.filters["candidateGroups"] == "group1, group2"
        q.filters.pop("candidateGroups")

        self.test_parameter(query.involved_user, "involvedUser", "sRuiz")
        self.test_parameter_with_like(query.task_definition_key,
                                      "taskDefinitionKey", "taskKey")

        self.test_parameter_object(query.process_instance,
                                   "processInstanceId", fake_object)
        self.test_parameter_with_like(query.process_instance_business_key,
                                      "processInstanceBusinessKey", "Bkey")
        self.test_parameter_with_like(query.process_definition_key,
                                      "processDefinitionKey", "processKey")
        self.test_parameter_with_like(query.process_definition_name,
                                      "processDefinitionName", "process name")
        self.test_parameter_object(query.execution, "executionId",
                                   fake_object)

        a_date = iso8601.parse_date("2013-04-17T10:17:43.902+0000")
        q = query.created_date(a_date)
        assert iso8601.parse_date(q.filters["createdOn"]) == a_date
        q.filters.pop("createdOn")

        q = query.created_date(a_date, "before")
        assert iso8601.parse_date(q.filters["createdBefore"]) == a_date
        q.filters.pop("createdBefore")

        q = query.created_date(a_date, "after")
        assert iso8601.parse_date(q.filters["createdAfter"]) == a_date
        q.filters.pop("createdAfter")

        q = query.due_date(None)
        assert q.filters.pop("withoutDueDate")

        q = query.due_date(a_date)
        assert iso8601.parse_date(q.filters["dueOn"]) == a_date
        q.filters.pop("dueOn")

        q = query.due_date(a_date, "before")
        assert iso8601.parse_date(q.filters["dueBefore"]) == a_date
        q.filters.pop("dueBefore")

        q = query.due_date(a_date, "after")
        assert iso8601.parse_date(q.filters.pop("dueAfter")) == a_date

        self.test_parameter_flag(query.exclude_subtasks, "excludeSubTasks")
        self.test_parameter_flag(query.active, "active")
        self.test_parameter_flag(query.include_task_local_variables,
                                 "includeTaskLocalVariables")
        self.test_parameter_flag(query.include_process_variables,
                                 "includeProcessVariables")

        self.test_parameter_with_like(query.tenant_id, "tenantId", "tenant")
        query = query.tenant_id(None)
        assert query.filters.pop("withoutTenantId") == True

        self.test_parameter(query.candidate_or_assigned, "candidateOrAssigned",
                            "sRuiz")

    @patch("pyactiviti.task_service.Query.list_post")
    def should_list_tasks(self, mock_list_post):

        self.query.process_definition_name("ProcessTestName")
        self.query.include_process_variables()

        mock_list_post.return_value = self.json_task_list

        task_list = self.query.list()
        assert len(task_list) == 2
        assert type(task_list[0]) == ts.Task
        mock_list_post.assert_any_call()
