import json
from pyactiviti.process_engine import ActivitiEngine
from pyactiviti import identity_service as ids
from requests.status_codes import codes

from pyactiviti.base import ResponseError
from unittest.mock import patch, Mock

import pytest
import pdb


class A_IdentityService:
    ACTIVITI_AUTH = ("kermit", "kermit")
    ACTIVITI_SERVICE = "http://localhost:8080/activiti-rest"
    IDENTITY_URL = ACTIVITI_SERVICE + "/identity/users"

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

    def setup_method(self, method):

        activiti_engine = ActivitiEngine(self.ACTIVITI_SERVICE,
                                         self.ACTIVITI_AUTH)
        self.identity_service = activiti_engine.identity_service

    def should_supply_new_user(self):
        user = self.identity_service.new_user("user1")

        assert user.__class__ == ids.User

    @patch("pyactiviti.identity_service.Service.get")
    def should_load_existing_user(self, mock_get):

        mock_get.return_value = self.get_json_user("user1")
        url = self.IDENTITY_URL + "/user1"

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

        url = self.IDENTITY_URL + "/user1"
        mock_get.side_effect = ResponseError(404)
        user = ids.User("user1")
        try:
            user = self.identity_service.load_user(user)
            pytest.fails("Exception should be raised")
        except ids.UserNotFound:
            mock_get.assert_called_with(url)

    @patch("pyactiviti.identity_service.Service.post")
    def should_save_new_user(self, mock_post):

        url = self.IDENTITY_URL

        login = "user1"
        json_user = self.get_json_user(login)

        user = self.get_user(login)
        assert self.identity_service.save_user(user)

        dict_user = json.loads(json_user)
        mock_post.assert_called_with(url, dict_user)

    @patch("pyactiviti.identity_service.Service.delete")
    def should_delete_user(self, mock_delete):
        url = self.IDENTITY_URL + "/user1"
        response = Mock()
        response.status_code = 204
        mock_delete.return_value = response

        user = self.get_user("user1")

        assert self.identity_service.delete_user(user).status_code == 204

        assert user._activiti_version == {}

        mock_delete.assert_called_with(url)

    @patch("pyactiviti.identity_service.Service.put")
    def should_update_user(self, mock_put):
        url = self.IDENTITY_URL + "/user1"
        response = Mock()
        response.status_code = 200
        json_user = self.get_json_user("user1")
        mock_put.return_value = response

        user = self.get_user("user1")

        assert self.identity_service.update_user(user)
        mock_put.assert_called_with(url, json.loads(json_user))

    @patch("pyactiviti.identity_service.Query.list")
    def should_list_users(self, mock_list):
        query = self.identity_service.create_user_query()

        assert query.session == self.identity_service.session
        assert query.url == self.IDENTITY_URL
        assert type(query) is ids.UserQuery


class A_UserQuery:

    activiti_engine = ActivitiEngine("http://localhost:8080/activiti-rest",
                                     ("kermit", "kermit"))
    identity_service = activiti_engine.identity_service

    def setup_method(self, method):
        self.query = self.identity_service.create_user_query()

    def should_add_parameters(self):
        name = "firstname"
        query = self.query.first_name(name)
        assert query.parameters["firstName"] == name

        name = "%firstname"
        self.query.first_name(name)
        assert query.parameters["firstNameLike"] == name

        name = "lastname"
        self.query.last_name(name)
        assert query.parameters["lastName"] == name

        name = "%lastname"
        self.query.last_name(name)
        assert query.parameters["lastNameLike"] == name

        name = "email"
        self.query.email(name)
        assert query.parameters["email"] == name

        name = "group"
        self.query.member_of_group(name)
        assert query.parameters["memberOfGroup"] == name

        name = "processDefinitionId"
        self.query.potential_starter(name)
        assert query.parameters["potentialStarter"] == name

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
