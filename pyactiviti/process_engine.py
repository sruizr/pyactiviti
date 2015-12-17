import json
from pyactiviti.identity_service import IdentityService
import requests


class ActivitiEngine:

    def __init__(self, endpoint, auth=('kermit', 'kermit')):
        self.endpoint = endpoint
        self.auth = auth

        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({'content-type': 'application/json'})
        self.identity_service = IdentityService(self)
        self.runtime_service = None
        self.task_service = None
