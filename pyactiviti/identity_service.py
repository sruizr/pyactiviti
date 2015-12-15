from .base import Service


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


class UserQuery(Query):
    pass


class IdentityService(Service):

    def __init__(self, engine):
        pass

    def new_user(self, user_id):
        return User(user_id)

    def load_user(self, user_id):
        pass

    def save_user(self, user):
        pass

    def delete_user(self, user):
        pass

    def update_user(self, user):
        pass

    def get_user_info(self, key):
        pass

    def set_user_info(self, key):
        pass

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
