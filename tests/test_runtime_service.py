from pyactiviti.runtime_service import (
                                        Execution,
                                        ProcessInstance,
                                        RuntimeService)
from pyactiviti.process_engine import ActivitiEngine
from unittest.mock import patch, Mock


Class A_RuntimeService:

    def setup_method(self, method):
        activiti_engine = ActivitiEngine("http://localhost:8080/rest")
        self.runtime_service = RuntimeService(activiti_engine)


    @patch("pyactiviti.runtime_service.Service.create")
    def should_start_a_process_instance(self, mock_create):
        process_instance = Execution()


        mock_create.return_value = """{
   "id":"7",
   "url":"http://localhost:8182/runtime/process-instances/7",
   "businessKey":"myBusinessKey",
   "suspended":false,
   "processDefinitionUrl":"http://localhost:8182/repository/process-definitions/processOne%3A1%3A4",
   "activityId":"processTask",
   "tenantId" : null
}"""

        self.runtime_service.start_process(process_instance)

        assert process_instance.id
        mock_create_assert
