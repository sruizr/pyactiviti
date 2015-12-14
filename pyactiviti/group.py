   group_url = lambda self, id: self.groups_url(id)

GROUPS_FIELDS = [
    'id', 'name', 'type', 'nameLike', 'member', 'potentialStarter', 'sort'
]


class Group:

    def __init__(self, id, name, type=None, member=None):
        self.id = id
        self.name = name
        self.member = member
        self.rest_connection = None

    def groups_url(self, *args):
        return self._to_endpoint('identity', 'groups', *args)

    def get_group(self, group_id):
        response = self.rest_connection.get(self.group_url(group_id))
        if response.status_code == codes.ok:
            return True
        elif response.status_code == codes.not_found:
            return False
        raise NotImplementedError()

    def groups(self, **parameters):
        params = check_parameters(GROUPS_FIELDS, parameters)

        response = self.rest_connection.get(self.groups_url(), params=params)
        if response.status_code == codes.ok:
            return response.json()

        raise NotImplementedError()

    def group_update(self, group_id, values=None):
        response = self.rest_connection.put(self.group_url(group_id), values=values)
        if response.status_code == codes.ok:
            return response.json()
        elif response.status_code == codes.not_found:
            raise GroupNotFound()
        elif response.status_code == codes.conflict:
            raise GroupUpdatedSimultaneous()

    def create_group(self, id, name, type):
        values = dict(id=id, name=name, type=type)
        response = self.rest_connection.post(self.groups_url(), values)
        if response.status_code == codes.created:
            return response.json()
        elif response.status_code == codes.bad_request:
            raise GroupMissingID()

    def delete_group(self, group_id):
        response = self.rest_connection.delete(self.group_url(group_id))

        if response.status_code == codes.no_content:
            return True
        elif response.status_code == codes.not_found:
            raise GroupNotFound()

    def group_add_member(self, group_id, user_id):
        values = {
            'userId': user_id,
        }
        response = self.rest_connection.post(
            self._to_endpoint('identity', 'groups', group_id, 'members'),
            values=values
        )
        if response.status_code == codes.created:
            return response.json()
        elif response.status_code == codes.not_found:
            raise GroupNotFound()
        elif response.status_code == codes.conflict:
            raise UserAlreadyMember()

    def group_remove_member(self, group_id, user_id):
        try:
            return self.rest_connection.delete(
                                               self._to_endpoint(
                                                                 'identity',
                                                                 'groups',
                                                                 group_id,
                                                                 'members',
                                                                 user_id
                                                                 )
                                               )
        except ResponseError as e:
            if e.status_code == codes.not_found:
                raise NotFound()
