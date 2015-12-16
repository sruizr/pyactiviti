import requests
import json
import pdb


def check_parameters(fields, args):
    arguments = {}
    for item in fields:
        value = args.pop(item, None)
        if value:
            arguments[item] = value
    return arguments


class Service:

    def __init__(self, engine):
        self.endpoint = engine.endpoint
        self.session = engine.session

    def delete(self, service):
        response = self.session.delete(service)
        if response.status_code == requests.codes.no_content:
            return True
        elif response.status_code == requests.codes.not_found:
            raise NotFound()

    def post(self, service, values=None):
        if values:
            values = json.dumps(values)
        return self.session.post(service, data=values)

    def get(self, service, params=None):
        response = self.session.get(service, params=params)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise ResponseError(response.status_code)

    def put(self, service, values=None):
        if values:
            values = json.dumps(values)
        return self.session.put(service, data=values)

    def to_endpoint(self, *args):
        return '/'.join([self.endpoint] + list(str(arg) for arg in args))


class Query:

    def count():
        pass

    def list():
        pass

    def single_result():
        pass


class ResponseError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class UpdatedSimultaneous(Exception):
    pass


class NotFound(Exception):
    pass


class MissingID(Exception):
    pass


class AlreadyExists(Exception):
    pass


