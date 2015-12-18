from pyactiviti.base import (
                             Service,
                             Query,
                             ResponseError,
                             AlreadyExists,
                             MissingID,
                             NotFound,
                             UpdatedSimultaneous,
                             JavaDictMapper,
                             )
from requests.status_codes import codes

import json

import pdb


class User:

    def __init__(self, id):
        self.id = id
        self.first_name = None
        self.last_name = None
        self.password = None
        self.email = None
        self._activiti_version = {}

    def is_syncronized(self):
        return self._activiti_version == JavaDictMapper.get_dict(self)


class Group:

    def __init__(self, id):
        self.id = id
        self.name = None
        self.type = None

    def is_syncronized(self):
        return self._activiti_version == JavaDictMapper.get_dict(self)


# class UserQuery(Query):
#     pass
class UserNotFound(Exception):
    pass


class UserAlreadyExists(AlreadyExists):
    pass


class UserMissingID(MissingID):
    pass


class UserUpdatedSimultaneous(UpdatedSimultaneous):
    pass


class UserAlreadyMember(Exception):
    pass


class GroupNotFound(NotFound):
    pass


class UserQuery(Query):

    def __init__(self, session, url):
        Query.__init__(self, session, url)

    def first_name(self, name):
        self._add_parameter_with_like("firstName") = name
        return self

    def email(self, name):
        if "%" in name:
            self.parameters["emailLike"] = name
        else:
            self.parameters["email"] = name
        return self

    def last_name(self, name):
        if "%" in name:
            self.parameters["lastNameLike"] = name
        else:
            self.parameters["lastName"] = name
        return self

    def member_of_group(self, group):
        self.parameters["memberOfGroup"] = group.id
        return self

    def potential_starter(self, process_definition):
        self.parameters["potentialStarter"] = process_definition.id
        return self

    def list(self):
        dict_result = super(UserQuery, self).list()
        user_list = []
        for dict_user in dict_result:
            user = User(dict_user["id"])
            JavaDictMapper.update_object(user, dict_user)
            user_list.append(user)

        return user_list

class GroupQuery(Query):

    def member(self, user):
        return self

    def group_name(self, name):
        return self

    def group_type(self, name):
        return self

    def potential_starters(self, ):
        return self

    def list(self):
        dict_result = super(UserQuery, self).list()
        user_list = []
        for dict_user in dict_result:
            user = User(dict_user["id"])
            JavaDictMapper.update_object(user, dict_user)
            user_list.append(user)

        return user_list


class IdentityService(Service):

    def __init__(self, engine):
        Service.__init__(self, engine)
        self.endpoint = self.endpoint + "/identity"

    def new_user(self, user_id):
        return User(user_id)

    def load_user(self, user):
        try:
            json_user = self.get(self.to_endpoint("users", user.id))
            dict_user = json.loads(json_user)
            user.first_name = dict_user["firstName"]
            user.last_name = dict_user["lastName"]
            user.email = dict_user["email"]
        except ResponseError as e:
            if e.status_code == 404:
                raise UserNotFound()
            else:
                raise e

        return user

    def save_user(self, user):

        dict_user = JavaDictMapper.get_dict(user)

        try:
            response = self.post(self.to_endpoint("users"), dict_user)
            user._activiti_version = user.__dict__
        except ResponseError as e:
            if e.status_code == codes.conflict:
                raise UserAlreadyExists(response.json()['exception'])
            elif e.status_code == codes.bad_request:
                raise UserMissingID()

        return True

    def delete_user(self, user):
        try:
            result = self.delete(self.to_endpoint("users", user.id))
            user._activiti_version = {}
        except ResponseError as e:
            if e.status_code == codes.not_found:
                raise UserNotFound()

        return result

    def update_user(self, user):
        dict_user = JavaDictMapper.get_dict(user)

        if not user.is_syncronized():
            response = self.put(self.to_endpoint("users", user.id), dict_user)
            if response.status_code == codes.ok:
                return response.json()
            if response.status_code == codes.not_found:
                raise UserNotFound()
            elif response.status_code == codes.conflict:
                raise UserUpdatedSimultaneous()

            return True

    def create_user_query(self):
        query_url = self.to_endpoint("users")
        user_query = UserQuery(self.session, query_url)

        return user_query

    def new_group(self, group_id):
        return Group(group_id)

    def save_group(self, group):
        dict_group = JavaDictMapper.get_dict(group)

        self.post(self.to_endpoint("groups"), dict_group)

        return True

    def delete_group(self, group):
        try:
            result = self.delete(self.to_endpoint("groups", group.id))
        except ResponseError as e:
            if e.status_code == codes.not_found:
                raise UserNotFound()

        return True

    def update_group(self, group):
        dict_group = JavaDictMapper.get_dict(group)

        response = self.put(self.to_endpoint("groups", group.id), dict_group)
        if response.status_code == codes.ok:
            return response.json()
        if response.status_code == codes.not_found:
            raise GroupNotFound()
        elif response.status_code == codes.conflict:
            raise GroupUpdatedSimultaneous()

        return True

    def create_membership(self, user, group):
        pass

    def delete_membership(self, user, group):
        pass

    def create_group_query(self):
        pass


