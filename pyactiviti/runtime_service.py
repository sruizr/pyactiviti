from .base import (
                   Query,
                   Service,
                   )


class Execution:
    pass


class ExecutionQuery(Query):
    pass


class RuntimeService(Service):

    def __init__(self, engine):
        Service.__init__(self, engine)

    def create_execution_query(self):
        return None

    def get_all_variables(self, execution):
        pass

    def set_variables(self, execution, **variables):
        pass

    def signal(execution, variables=None):
        pass

    def start_process_instance(self, variables):
        pass
