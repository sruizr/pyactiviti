USERS_FIELDS = [
    'id', 'firstName', 'lastName', 'email', 'firstNameLike',
    'lastNameLike', 'emailLike', 'memberOfGroup', 'potentialStarter',
    'sort'
]
from . import base as b


class User:

    def __init__(self, id, email=None, password=None, firstname=None,
                 lastname=None):
        self.id = id
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.rest_connection = None
        self.user_url = lambda self, id: self.users_url(id)

    def users_url(self, *args):
        return self.rest_connection.to_endpoint('identity', 'users', *args)

    def exists(self, login):
        response = self.rest_connection.get(self.user_url(login))
        return response.status_code == codes.ok

    def create(self, login, email, password, firstname=None, lastname=None):
        user = {
            'id': login,
            'email': email,
            'password': password,
            'firstName': firstname or '',
            'lastName': lastname or ''
        }
        response = self.rest_connection.post(self.users_url(), user)
        if response.status_code == codes.created:
            return response.json()
        elif response.status_code == codes.conflict:
            raise UserAlreadyExists(response.json()['exception'])
        elif response.status_code == codes.bad_request:
            raise UserMissingID()

        return response.status_code == codes.created

    def user(self, user_id, values=None):
        response = self.rest_connection.put(self.user_url(user_id), values=values)
        if response.status_code == codes.ok:
            return response.json()
        elif response.status_code == codes.not_found:
            raise UserNotFound()
        elif response.status_code == codes.conflict:
            raise UserUpdatedSimultaneous()


    def delete(self, login):
        response = self.rest_connection.delete(self.user_url(login))
        if response.status_code == codes.no_content:
            return True
        elif response.status_code == codes.not_found:
            raise UserNotFound()

    @classmethod
    def get_by_id(cls, id):
        response = self.rest_connection.get(self.user_url(id))
        if response.status_code == codes.ok:
            return response.json()
        raise UserNotFound()


    @classmethod
    def query_users(self, **parameters):
        params = b.check_parameters(USERS_FIELDS, parameters)

        response = self.rest_connection.get(self.users_url(), params=params)
        if response.status_code == codes.ok:
            return response.json()
        raise NotImplementedError()

    @classmethod
    def get_users_member_of(self, group):
        return self.users(memberOfGroups=group)

