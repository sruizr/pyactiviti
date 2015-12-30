import requests
from requests.status_codes import codes
import json
import re
from collections import UserDict
import pdb


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


class Variables(UserDict):

    def __init__(self, rest_data=None, **kwargs):
        """rest_data is a dictionary with format of Rest variables"""
        UserDict.__init__(self, **kwargs)
        self.rest_data = None
        if rest_data:
            self.load(rest_data)

    def load(self, rest_data):
        for variable in rest_data:
            name = self._var_name(variable["name"], variable["scope"])
            self.data[name] = variable["value"]
        self.rest_data = rest_data

    def sync_rest(self):
        result = []
        dict_rest = {}
        for item in rest_data:
            dict_rest[self._var_name(item["name"], item["scope"])] = item

        # data vs dict_rest
        for key, value in data:
            if key not in dict_rest:  # new variable
                is_local = key[-1] == "_"
                scope = "local" if is_local else "global"
                name = key
                if is_local:
                        name[-1] = None
                result.append({"name": name, "scope": scope, "value": value})

        return result

    @staticmethod
    def _var_name(name, scope):
        res = name
        if scope == "local":
            res += "_"
        return res





class Service:

    def __init__(self, engine, url=None):
        self.rest_url = engine.rest_url
        if url:
            self.url = self.rest_url + "/" + url

        self.session = engine.session

    def create(self, obj, *path):
        url = self._to_endpoint(*path)
        values = json.dumps(obj)
        response = self.session.post(url, data=values)
        # pdb.set_trace()
        if response.status_code == codes.bad_request:
            raise MissingID()
        if response.status_code != codes.created:
            raise UnknownError()

    def update(self, obj, *path):
        url = self._to_endpoint(*path)
        values = json.dumps(obj)
        response = self.session.put(url, data=values)

        if response.status_code == codes.not_found:
            raise NotFound()
        if response.status_code == codes.conflict:
            raise UpdatedSimultaneous()
        if response.status_code != codes.ok:
            raise UnknownError()

    def load(self, *path):
        url = self._to_endpoint(*path)
        response = self.session.get(url)
        if response.status_code == codes.not_found:
            raise NotFound()
        if response.status_code != requests.codes.ok:
            raise UnknownError()

        return response.json()

    def delete(self, *path):
        url = self._to_endpoint(*path)
        response = self.session.delete(url)
        if response.status_code == requests.codes.not_found:
            raise NotFound()
        if response.status_code != codes.no_content:
            raise UnknownError()

    def post_with_json(self, values, *path):
        url = self._to_endpoint(*path)
        values = json.dumps(values)
        response = self.session.post(url, data=values)
        # pdb.set_trace()
        if response.status_code == codes.bad_request:
            raise MissingID()
        if response.status_code != codes.created:
            raise UnknownError()

    def _to_endpoint(self, *args):
        return '/'.join([self.url] +
                        list(str(arg) for arg in args))


class Query:

    def __init__(self, engine, url_path, post=True):
        self.engine = engine
        self.url = engine.rest_url + url_path
        self.session = engine.session
        self.parameters = {}
        self.variable_parameter = []

    def count(self):
        pass

    def list_get(self):
        response = self.session.get(self.url, params=self.parameters)
        return response.json()

    def list_post(self):
        response = self.session.post(self.url, data=self.parameters)
        return response.json()

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

    def _add_process_variable(self, name, value, operator="equals"):
        valid_operators = ("equals", "notEquals", "equalsIgnoreCase",
                           "notEqualsIgnoreCase", "lessThan", "greaterThan",
                           "greaterThanOrEquals", "lessThanOrEquals", "like")

        if operator in valid_operators:
            variable_parameter = {"name": name,
                                                "value": value,
                                                "operation": operator}
            self.variable_parameter.append(variable_parameter)
        else:
            raise IncorrectOperator()


class IncorrectOperator(Exception):
    pass


class UpdatedSimultaneous(Exception):
    pass


class NotFound(Exception):
    pass


class MissingID(Exception):
    pass


class AlreadyExists(Exception):
    pass


class UnknownError(Exception):
    pass
