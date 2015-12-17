# -*- coding: utf-8 -*-
import requests
import json
from requests.status_codes import codes
from .base import ResponseError
from .exceptions import (
    UserAlreadyExists,
    NotFound,
    UserNotFound,
    GroupNotFound,
    GroupMissingID,
    UserMissingID,
    GroupUpdatedSimultaneous,
    UserAlreadyMember,
    UserUpdatedSimultaneous,
    DeploymentNotFound
)

DEPLOYMENTS_FIELDS = [
    'name', 'nameLike', 'category', 'categoryNotEquals', 'tenantId',
    'tenantIdLike', 'withoutTenantId', 'sort'
]


class Activiti(object):
    def process_definitions(self):
        response = self.rest_connection.get('/repository/process-definitions')
        return json.loads(response.content)

    def start_process_by_key(self, key, variables=None):
        if variables is None:
            variables = {}

        variables = [
            {'name': _key, 'value': value}
            for _key, value in variables.iteritems()
        ]
        values = {
            'processDefinitionKey': key,
            'businessKey': 'business%s' % key,
            'variables': variables,
        }
        return self.rest_connection.post('/runtime/process-instances', values)

    def get_user_task_list(self, user, process=None):
        url = '/runtime/tasks?involvedUser=%s' % (user,)
        if process:
            url += '&processDefinitionKey=%s' % (process,)

        response = self.rest_connection.get(url)
        return json.loads(response.content)

    def get_task_form(self, task_id):
        response = self.rest_connection.get(
                                            '/form/form-data?taskId=%s' % (task_id,))
        return json.loads(response.content)

    def submit_task_form(self, task_id, properties=None):
        if properties is None:
            properties = {}

        properties = [
            {'id': _key, 'value': value}
            for _key, value in properties.iteritems()
        ]

        codes.

        values = {
            'taskId': task_id,
            'properties': properties,
        }
        return self.rest_connection.post('/form/form-data', values)
