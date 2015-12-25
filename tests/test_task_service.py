import json
import pyactiviti.task_service as ts
from pyactiviti.process_engine import ActivitiEngine
import pyactiviti.base as b
from unittest.mock import Mock, patch
from .base import TestQuery
import pdb
import pytest
import iso8601


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
  "tenantId" : null
}"""
        dict_task = json.loads(json_task)
        ref_time = iso8601.parse_date("2013-04-17T10:17:43.902+0000")

        task = ts.Task("8")
        task.parse(dict_task)
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
  "tenantId" : null
}"""
        return json.loads(json_task)

    def get_task(self):
        task = ts.Task("8")
        task.parse(self.get_dict_task())

        return task

    def should_has_correct_url_base(self):
        assert self.task_service.url == "http://localhost:8080/runtime"

    @patch("pyactiviti.task_service.Service.load")
    def should_load_task(self, mock_load):
        mock_load.return_value = self.get_dict_task()

        task = ts.Task("8")
        self.task_service.load_task(task)

        expected_task = self.get_task()
        assert task.description == expected_task.description
        assert task.id == expected_task.id

    @patch("pyactiviti.task_service.Service.load")
    def should_raise_exception_when_loading_unexisting_task(self, mock_load):
        mock_load.side_effect = b.NotFound()

        task = ts.Task("10")
        with pytest.raises(ts.TaskNotFound):
            self.task_service.load_task(task)

    def should_supply_task_query(self):
        pass


class A_TaskQuery(TestQuery):

    def setup_method(self, method):
        engine = ActivitiEngine("http://localhost:8080/rest_engine")
        self.query = ts.TaskQuery(engine)

    def should_be_initialized_with_service(self):
        assert not self.query.parameters
        assert self.query.url == "http://localhost:8080/rest_engine/query/tasks"

    def should_add_parameters_to_task(self):
        fake_object = Mock()
        fake_object.id = "objectId"
        self.test_parameter_with_like(self.query.name, "name", "a name")
        self.test_parameter(self.query.description, "description",
                            "task description")
        self.test_parameter_numerical(self.query.priority, "minimumPriority",
                                      "greater", 12)
        self.test_parameter(self.query.priority, "priority", 10)
        self.test_parameter_numerical(self.query.priority, "maximumPriority",
                                      "less", 10)
        self.test_parameter_with_like(self.query.assignee, "assignee", "sRuiz")

        q = self.query.assignee(None)
        assert q.parameters["unassigned"] == True
        q.parameters.pop("unassigned")

        self.test_parameter_with_like(self.query.owner, "owner", "sRuiz")
        self.test_parameter(self.query.delegation_state, "delegationState",
                            "pending")
        self.test_parameter(self.query.delegation_state, "delegationState",
                            "resolved")
        q = self.query.delegation_state("nostate")
        assert "unassigned" not in q.parameters

        self.test_parameter(self.query.candidate_user, "candidateUser",
                            "sRuiz")
        self.test_parameter(self.query.candidate_group, "candidateGroup",
                            "testGroup")
        q = self.query.candidate_group("group1", "group2")
        assert q.parameters["candidateGroups"] == "group1, group2"
        q.parameters.pop("candidateGroups")

        self.test_parameter(self.query.involved_user, "involvedUser", "sRuiz")
        self.test_parameter_with_like(self.query.task_definition_key,
                                      "taskDefinitionKey", "taskKey")

        self.test_parameter_object(self.query.process_instance,
                                   "processInstanceId", fake_object)
        self.test_parameter_with_like(self.query.process_instance_business_key,
                                      "processInstanceBusinessKey", "Bkey")
        self.test_parameter_with_like(self.query.process_definition_key,
                                      "processDefinitionKey", "processKey")
        self.test_parameter_with_like(self.query.process_definition_name,
                                      "processDefinitionName", "process name")
        self.test_parameter_object(self.query.execution, "executionId",
                                   fake_object)
