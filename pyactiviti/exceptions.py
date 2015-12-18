

class DeploymentNotFound(NotFound):
    pass


class BadQueryParameters(Exception):
    pass


class GroupMissingID(MissingID):
    pass


class GroupUpdatedSimultaneous(UpdatedSimultaneous):
    pass


