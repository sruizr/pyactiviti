import json
from pyactiviti.identity_service import IdentityService
from pyactiviti.task_service import TaskService
import requests


class ActivitiEngine:

    def __init__(self, rest_url, auth=('kermit', 'kermit')):
        self.rest_url = rest_url
        self.auth = auth

        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({'content-type': 'application/json'})
        self.identity_service = IdentityService(self)
        self.runtime_service = None
        self.task_service = TaskService(self)
