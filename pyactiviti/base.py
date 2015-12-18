import requests
import json
import re
import pdb


def check_parameters(fields, args):
    arguments = {}
    for item in fields:
        value = args.pop(item, None)
        if value:
            arguments[item] = value
    return arguments


class JavaDictMapper:
    """It converts any object with it's attributes to a dictionary
    with camelCase keys"""

    @classmethod
    def get_dict(self, object):
        result = object.__dict__.copy()
        keys = list(result.keys())
        for key in keys:
            if key[0] == "_":  # internal parameters are not mapped
                result.pop(key)
            else:
                result[self.to_camel_case(key)] = result.pop(key)
        return result

    @classmethod
    def update_object(self, obj, java_dict):
        for key in java_dict.keys():
            if key != "url":
                setattr(obj, self.to_snake(key), java_dict[key])

    @classmethod
    def to_snake(self, camel_case):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @classmethod
    def to_camel_case(self, snake):
        first, *rest = snake.split('_')
        return first + ''.join(word.capitalize() for word in rest)


class Service:

    def __init__(self, engine):
        self.endpoint = engine.endpoint
        self.session = engine.session

    def delete(self, url):
        response = self.session.delete(url)
        if response.status_code == requests.codes.no_content:
            return True
        elif response.status_code == requests.codes.not_found:
            raise NotFound()

    def post(self, url, values=None):
        if values:
            values = json.dumps(values)
        return self.session.post(url, data=values)

    def get(self, url, params=None):
        response = self.session.get(url, params=params)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise ResponseError(response.status_code)

    def put(self, url, values=None):
        if values:
            values = json.dumps(values)
        return self.session.put(url, data=values)

    def to_endpoint(self, *args):
        return '/'.join([self.endpoint] + list(str(arg) for arg in args))


class Query:

    def __init__(self, session, url):
        self.url = url
        self.session = session
        self.parameters = {}

    def count(self):
        pass

    def list(self):
        pass

    def single_result(self):
        pass

    def _add_parameter(self, name, value):
        self.parameters[name] = value

    def _add_parameter_with_like(self, name, value):
        if "%" in value:
            self.parameters[name + "Like"] = value
        else:
            self.parameters[name] = value

    def _add_parameter_object(self, name, obj):
        self.parameters[name] = obj.id


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
