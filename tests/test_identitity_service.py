import json
from pyactiviti.process_engine import ActivitiEngine
from pyactiviti import identity_service as ids
from requests.status_codes import codes

from pyactiviti.base import ResponseError
from unittest.mock import patch, Mock
from .base import TestQuery

import pytest
import pdb


class A_IdentityService:
    ACTIVITI_AUTH = ("kermit", "kermit")
    ACTIVITI_SERVICE = "http://localhost:8080/activiti-rest"
    IDENTITY_URL = ACTIVITI_SERVICE + "/identity"

    def get_json_user(self, login):
        user = {
            "id": login,
            "firstName": "Fred",
            "lastName": "McDonald",
            "email": "no-reply@activiti.org",
            "password": None
            }
        return json.dumps(user)

    def get_user(self, login):
        json_user = json.loads(self.get_json_user(login))

        user = ids.User(login)
        user.first_name = json_user["firstName"]
        user.last_name = json_user["lastName"]
        user.email = json_user["email"]
        user.password = json_user["password"]

        return user

    def get_group(self):
        group = ids.Group("testGroup")
        group.name = "Test group"
        group.type = "Test type"

        return group

    def get_json_group(self):
        group = """{
   "id":"testGroup",
   "name":"Test group",
   "type":"Test type"
}"""

        return group

    def setup_method(self, method):

        activiti_engine = ActivitiEngine(self.ACTIVITI_SERVICE,
                                         self.ACTIVITI_AUTH)
        self.identity_service = activiti_engine.identity_service


    # User related services
    def should_supply_new_user(self):
        user = self.identity_service.new_user("user1")

        assert user.__class__ == ids.User

    @patch("pyactiviti.identity_service.Service.get")
    def should_load_existing_user(self, mock_get):

        mock_get.return_value = self.get_json_user("user1")
        url = self.IDENTITY_URL + "/users/user1"

        user = ids.User("user1")
        user = self.identity_service.load_user(user)
        fake_user = self.get_user("user1")

        mock_get.assert_called_with(url)
        assert user.id == fake_user.id
        assert user.first_name == fake_user.first_name
        assert user.last_name == fake_user.last_name
        assert user.email == fake_user.email

    @patch("pyactiviti.identity_service.Service.get")
    def should_raise_exception_loading_unexisting_user(self, mock_get):

        url = self.IDENTITY_URL + "/users/user1"
        mock_get.side_effect = ResponseError(404)
        user = ids.User("user1")
        try:
            user = self.identity_service.load_user(user)
            pytest.fails("Exception should be raised")
        except ids.UserNotFound:
            mock_get.assert_called_with(url)

    @patch("pyactiviti.identity_service.Service.post")
    def should_save_new_user(self, mock_post):

        url = self.IDENTITY_URL + "/users"

        login = "user1"
        json_user = self.get_json_user(login)

        user = self.get_user(login)
        assert self.identity_service.save_user(user)

        dict_user = json.loads(json_user)
        mock_post.assert_called_with(url, dict_user)

    @patch("pyactiviti.identity_service.Service.delete")
    def should_delete_user(self, mock_delete):
        url = self.IDENTITY_URL + "/users/user1"
        response = Mock()
        response.status_code = 204
        mock_delete.return_value = response

        user = self.get_user("user1")

        assert self.identity_service.delete_user(user).status_code == 204

        assert user._activiti_version == {}

        mock_delete.assert_called_with(url)

    @patch("pyactiviti.identity_service.Service.put")
    def should_update_user(self, mock_put):
        url = self.IDENTITY_URL + "/users/user1"
        response = Mock()
        response.status_code = 200
        json_user = self.get_json_user("user1")
        mock_put.return_value = response

        user = self.get_user("user1")

        assert self.identity_service.update_user(user)
        mock_put.assert_called_with(url, json.loads(json_user))

    @patch("pyactiviti.identity_service.Query.list")
    def should_supply_user_query(self, mock_list):
        query = self.identity_service.create_user_query()

        assert query.session == self.identity_service.session
        assert query.url == self.IDENTITY_URL + "/users"
        assert type(query) is ids.UserQuery

    # Group related services
    def should_give_new_group(self):

        group = self.identity_service.new_group("testGroup")
        assert type(group) is ids.Group
        assert group.id == "testGroup"

    @patch("pyactiviti.identity_service.Service.post")
    def should_save_group(self, mock_post):
        group = self.get_group()
        json_group = json.loads(self.get_json_group())
        url = self.ACTIVITI_SERVICE + "/identity/groups"

        mock_response = Mock()
        mock_response.json.return_value = json_group
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        assert self.identity_service.save_group(group)
        mock_post.assert_called_with(url, json_group)

    @patch("pyactiviti.identity_service.Service.delete")
    def should_delete_group(self, mock_delete):
        url = self.ACTIVITI_SERVICE + "/identity/groups" + "/testGroup"
        response = Mock()
        response.status_code = 204
        mock_delete.return_value = response

        group = self.get_group()

        assert self.identity_service.delete_group(group)

        mock_delete.assert_called_with(url)

    @patch("pyactiviti.identity_service.Service.put")
    def should_update_group(self, mock_put):
        url = self.IDENTITY_URL + "/groups/testGroup"
        response = Mock()
        response.status_code = 200
        json_group = self.get_json_group()
        mock_put.return_value = response

        group = self.get_group()

        assert self.identity_service.update_group(group)
        mock_put.assert_called_with(url, json.loads(json_group))

    @patch("pyactiviti.identity_service.Service.post")
    def should_create_membership(self, mock_post):
        url = self.IDENTITY_URL + "/groups/testGroup/members"
        json_user = """{
   "userId":"kermit"
}"""
        json_user = json.loads(json_user)
        user = self.get_user("kermit")
        group = self.get_group()

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = """{
   "userId":"kermit",
   "groupId":"testGroup",
    "url":"http://localhost:8182/identity/groups/testGroup/members/kermit"
}"""
        mock_post.return_value = mock_response

        assert self.identity_service.create_membership(user, group)
        mock_post.assert_called_with(url, json_user)

    @patch("pyactiviti.identity_service.Service.delete")
    def should_delete_membership(self, mock_del):
        url = self.IDENTITY_URL + "/groups/testGroup/members/kermit"
        json_user = """{
   "userId":"kermit"
}"""
        json_user = json.loads(json_user)
        user = self.get_user("kermit")
        group = self.get_group()

        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = """{
   "userId":"kermit",
   "groupId":"testGroup",
    "url":"http://localhost:8182/identity/groups/testGroup/members/kermit"
}"""
        mock_del.return_value = mock_response

        assert self.identity_service.delete_membership(user, group)
        mock_del.assert_called_with(url)

    @patch("pyactiviti.identity_service.Query.list")
    def should_supply_group_query(self, mock_list):
        query = self.identity_service.create_group_query()

        assert query.session == self.identity_service.session
        assert query.url == self.IDENTITY_URL + "/groups"
        assert type(query) is ids.GroupQuery


class A_UserQuery(TestQuery):

    activiti_engine = ActivitiEngine("http://localhost:8080/activiti-rest",
                                     ("kermit", "kermit"))
    identity_service = activiti_engine.identity_service

    def setup_method(self, method):
        self.query = self.identity_service.create_user_query()

    def should_add_parameters(self):
        self.test_parameter_with_like(self.query.first_name,
                                      "firstName", "first name")

        self.test_parameter_with_like(self.query.last_name,
                                      "lastName", "last name")

        self.test_parameter_with_like(self.query.email,
                                      "email", "email@email.com")

        query = self.query

        group = ids.Group("groupId")
        self.query.member_of_group(group)
        assert query.parameters["memberOfGroup"] == group.id

        process_definition = ids.Group("fakeObject")
        self.query.potential_starter(process_definition)
        assert query.parameters["potentialStarter"] == process_definition.id

    @patch("pyactiviti.identity_service.Query.list")
    def should_list_users(self, mock_list):
        list_result = """{
   "data":[
      {
         "id":"anotherUser",
         "firstName":"Tijs",
         "lastName":"Barrez",
         "url":"http://localhost:8182/identity/users/anotherUser",
         "email":"no-reply@alfresco.org"
      },
      {
         "id":"kermit",
         "firstName":"Kermit",
         "lastName":"the Frog",
         "url":"http://localhost:8182/identity/users/kermit",
         "email":null
      },
      {
         "id":"testuser",
         "firstName":"Fred",
         "lastName":"McDonald",
         "url":"http://localhost:8182/identity/users/testuser",
         "email":"no-reply@activiti.org"
      }
   ],
   "total":3,
   "start":0,
   "sort":"id",
   "order":"asc",
   "size":3
}"""
        list_result = json.loads(list_result)["data"]
        mock_list.return_value = list_result
        users = self.query.list()

        user = users[0]
        assert type(user) is ids.User
        assert user.id == "anotherUser"
        assert user.first_name == "Tijs"
        assert user.last_name == "Barrez"
        assert user.email == "no-reply@alfresco.org"

        assert users[1].id == "kermit"
        assert users[2].id == "testuser"


class A_GroupQuery(TestQuery):

    activiti_engine = ActivitiEngine("http://localhost:8080/activiti-rest",
                                     ("kermit", "kermit"))
    identity_service = activiti_engine.identity_service

    def setup_method(self, method):
        self.query = self.identity_service.create_group_query()

    def should_add_parameters(self):
        self.test_parameter_with_like(self.query.group_name, "name",
                                      "Test group name")
        self.test_parameter(self.query.group_type, "type", "Test type group")

        user = ids.User("username")
        self.test_parameter_object(self.query.member, "member", user)

        fake_process_definition = ids.Group("process_key")
        self.test_parameter_object(self.query.potential_starter,
                                   "potentialStarter", fake_process_definition)

    @patch("pyactiviti.identity_service.Query.list")
    def should_list_groups(self, mock_list):
        list_result = """{
   "data":[
     {
        "id":"testgroup1",
        "url":"http://localhost:8182/identity/groups/testgroup",
        "name":"Test group1",
        "type":"Test type1"
     },
      {
        "id":"testgroup2",
        "url":"http://localhost:8182/identity/groups/testgroup",
        "name":"Test group2",
        "type":"Test type2"
     },
      {
        "id":"testgroup3",
        "url":"http://localhost:8182/identity/groups/testgroup",
        "name":"Test group3",
        "type":"Test type3"
     }
   ],
   "total":3,
   "start":0,
   "sort":"id",
   "order":"asc",
   "size":3
}"""
        list_result = json.loads(list_result)
        list_result = list_result["data"]
        mock_list.return_value = list_result
        groups = self.query.list()

        group = groups[0]
        assert type(group) is ids.Group
        assert group.id == "testgroup1"
        assert group.name == "Test group1"
        assert group.type == "Test type1"

        assert groups[1].id == "testgroup2"
        assert groups[2].id == "testgroup3"
