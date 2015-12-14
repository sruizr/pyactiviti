import requests
import json
from requests.status_codes import codes


def check_parameters(fields, args):
    arguments = {}
    for item in fields:
        value = args.pop(item, None)
        if value:
            arguments[item] = value
    return arguments


class RestConnection:

    def __init__(self, endpoint, auth=('kermit', 'kermit')):
        self.endpoint = endpoint
        self.auth = auth

        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({'content-type': 'application/json'})

    def delete(self, service):
        response = self.session.delete(service)
        if response.status_code == codes.no_content:
            return True
        elif response.status_code == codes.not_found:
            raise NotFound()

    def post(self, service, values=None):
        if values:
            values = json.dumps(values)
        return self.session.post(service, data=values)

    def get(self, service, params=None):
        response = self.session.get(service, params=params)
        if response.status_code == codes.ok:
            return response.json()
        else:
            raise RequestError(response.status_code)

    def put(self, service, values=None):
        if values:
            values = json.dumps(values)
        return self.session.put(service, data=values)

    def to_endpoint(self, *args):
        return '/'.join([self.endpoint, 'service'] + list(str(arg) for arg in args))


class ResponseError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
