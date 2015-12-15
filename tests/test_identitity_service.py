import json
from pyactiviti.process_engine import ActivitiEngine
from pyactiviti import identity_service as ids
import requests.status_codes as codes

import responses
import pytest


class A_IdentityService:
    ACTIVITI_AUTH = ('kermit', 'kermit')
    ACTIVITI_SERVICE = 'http://localhost:8080/activiti-rest'
    IDENTITY_URL = ACTIVITI_SERVICE + "/identity/users/"

    def fake_user(self, login):
        return {
            "id": login,
            "firstName": "Fred",
            "lastName": "McDonald",
            "url": "http://localhost:8080/activiti-rest/identity/users/" + login,
            "email": "no-reply@activiti.org"
            }

    def setup_method(self, method):

        activiti_engine = ActivitiEngine(self.ACTIVITI_SERVICE,
                                         self.ACTIVITI_AUTH)
        self.identity_service = activiti_engine.identity_service

    def should_supply_new_user(self):
        user = self.identity_service.new_user("user1")

        assert user.__class__ == ids.User

    @responses.activate
    def should_load_existing_user(self):

        responses.add(responses.GET, self.IDENTITY_URL + "user1",
                      json=self.fake_user("user1"), status=404)

        user = ids.User("user1")
        user = self.identity_service.load_user(user)
        fake_user = self.fake_user("user1")

        assert user.id == fake_user["id"]
        assert user.first_name == fake_user["firstName"]
        assert user.last_name == fake_user["lastName"]
        assert user.email == fake_user["email"]



