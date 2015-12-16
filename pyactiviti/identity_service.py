from pyactiviti.base import Service, ResponseError
from requests.status_code import codes


import json

import pdb


class User:

    def __init__(self, id):
        self.id = id
        self.first_name = None
        self.last_name = None
        self.password = None
        self.email = None


class Group:

    def __init__(self, id):
        self.id = id
        self.name = None
        self.type = None


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


class IdentityService(Service):

    def __init__(self, engine):
        Service.__init__(self, engine)
        self.endpoint = self.endpoint + "/identity"

    def new_user(self, user_id):
        return User(user_id)

    def load_user(self, user):
        try:
            dict_user = self.get(self.to_endpoint("users", user.id))
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
        json_user = {
            'id': user.id,
            'email': user.email,
            'password': user.pasword,
            'firstName': user.first_name,
            'lastName': user.last_name
        }

        try:
            response = self.rest_connection.post(self.users_url(), json_user)
        except ResponseError as e:
            if e.status_code == codes.conflict:
                raise UserAlreadyExists(response.json()['exception'])
            elif e.status_code == codes.bad_request:
                raise UserMissingID()

        return True

    def delete_user(self, user):
        try:
            result = self.rest_connection.delete(self.user_url(login))
        except ResponseError as e:
            if e.status_code == codes.not_found:
                raise UserNotFound()

        return result

    def update_user(self, user):
       response = self.rest_connection.put(self.user_url(user_id), values=values)        if response.status_code == codes.ok:
            return response.json()
        elif response.status_code == codes.not_found:
            raise UserNotFound()
        elif response.status_code == codes.conflict:
            raise UserUpdatedSimultaneous()

    def create_user_query(self):
        pass

    def new_group(self, group_id):
        return Group(group_id)

    def save_group(self, group):
        pass

    def create_group_query(self):
        pass

    def delete_group(self, group):
        pass

    def create_membership(self, user, group):
        pass

    def delete_membership(self, user, group):
        pass
