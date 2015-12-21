import json
from requests.status_codes import codes

from pyactiviti.base import (
                             Service,
                             Query,
                             AlreadyExists,
                             MissingID,
                             NotFound,
                             UpdatedSimultaneous,
                             JavaDictMapper,
                             )

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


class UserQuery(Query):

    def __init__(self, session, url):
        Query.__init__(self, session, url)

    def first_name(self, name):
        self._add_parameter_with_like("firstName", name)
        return self

    def email(self, name):
        self._add_parameter_with_like("email", name)
        return self

    def last_name(self, name):
        self._add_parameter_with_like("lastName", name)
        return self

    def member_of_group(self, group):
        self._add_parameter("memberOfGroup", group.id)
        return self

    def potential_starter(self, process_definition):
        self._add_parameter("potentialStarter", process_definition.id)
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

    def __init__(self, session, url):
        Query.__init__(self, session, url)

    def member(self, user):
        self._add_parameter_object("member", user)
        return self

    def group_name(self, name):
        self._add_parameter_with_like("name", name)
        return self

    def group_type(self, name):
        self._add_parameter("type", name)
        return self

    def potential_starter(self, process_definition):
        self._add_parameter_object("potentialStarter", process_definition)
        return self

    def list(self):
        dict_result = super(GroupQuery, self).list()
        group_list = []
        for dict_group in dict_result:
            group = Group(dict_group["id"])
            JavaDictMapper.update_object(group, dict_group)
            group_list.append(group)

        return group_list


class IdentityService(Service):

    def __init__(self, engine):
        Service.__init__(self, engine, "identity")

    def new_user(self, user_id):
        return User(user_id)

    def load_user(self, user):
        try:
            dict_user = self.load("users", user.id)
            JavaDictMapper.update_object(user, dict_user)
            return user
        except NotFound:
            raise UserNotFound()

    def create_user(self, user):
        try:
            dict_user = JavaDictMapper.get_dict(user)
            self.create(dict_user, "users")
            user._activiti_version = user.__dict__
        except MissingID:
            raise UserMissingID()

    def delete_user(self, user):
        try:
            self.delete("users", user.id)
            user._activiti_version = {}
        except NotFound:
            raise UserNotFound()

    def update_user(self, user):
        dict_user = JavaDictMapper.get_dict(user)
        try:
            self.update(dict_user, "users", user.id)
        except NotFound:
            raise UserNotFound()
        except UpdatedSimultaneous:
            raise UserUpdatedSimultaneous()

    def create_user_query(self):
        query_url = self._to_endpoint("users")
        user_query = UserQuery(self.session, query_url)
        return user_query

    def new_group(self, group_id):
        return Group(group_id)

    def load_group(self, group):
        try:
            dict_group = self.load("groups", group.id)
            JavaDictMapper.update_object(group, dict_group)
        except NotFound:
            raise GroupNotFound()

    def create_group(self, group):
        try:
            dict_group = JavaDictMapper.get_dict(group)
            self.create(dict_group, "groups")
        except MissingID:
            raise GroupMissingID()

    def delete_group(self, group):
        try:
            self.delete("groups", group.id)
        except NotFound:
            raise GroupNotFound()

    def update_group(self, group):
        try:
            dict_group = JavaDictMapper.get_dict(group)
            self.update(dict_group, "groups", group.id)
        except NotFound:
            raise GroupNotFound()
        except UpdatedSimultaneous:
            raise GroupUpdatedSimultaneous()

    def add_membership(self, user, group):
        dict_membership = {"userId": user.id}
        try:
            self.post_with_json(dict_membership, "groups", group.id, "members")
        except NotFound:
            raise NotFound()
        except UpdatedSimultaneous:
            raise MemberAlreadyExist()

    def remove_membership(self, user, group):
        try:
            self.delete("groups", group.id, "members", user.id)
        except NotFound:
            raise NotFound()

    def create_group_query(self):
        return GroupQuery(self.session, self._to_endpoint("groups"))


# Exceptions
class UserNotFound(NotFound):
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


class GroupMissingID(MissingID):
    pass


class GroupUpdatedSimultaneous(UpdatedSimultaneous):
    pass

class MemberAlreadyExist(UpdatedSimultaneous):
    pass
