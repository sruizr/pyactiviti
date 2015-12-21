from pyactiviti.base import (
                             Service,
                             Query,
                             JavaDictMapper,
                             )
import time


class Task:
    def __init__(self, id):
        self.id = id

    def parse(self, dict_task):
        JavaDictMapper.update_object(self, dict_task)
        self
        self.create_time = self._convert_to_time(self.create_time)
        self.due_date = self._convert_to_time(self.due_date)

        print(self.create_time)

    def _convert_to_time(self, str):
        str = str[0:len(str)-9]
        return time.strptime(str, "%Y-%m-%dT%H:%M:%S")

class TaskService(Service):

    def __init__(self, engine):
        Service.__init__(engine, "runtime")

    def load_task(self, task):
        dict_task = self.load("tasks", task.id)
        task.parse(dict_task)




class TaskQuery(Query):
    pass
