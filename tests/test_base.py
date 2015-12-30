from pyactiviti.base import (
                             JavaDictMapper,
                             Service,
                             Query,
                             MissingID,
                             NotFound,
                             UpdatedSimultaneous,
                             Variables,
                             )
from pyactiviti.process_engine import ActivitiEngine

from unittest.mock import Mock, patch
import json
import pdb
import pytest


class A_Service:
    def setup_method(self, method):
        engine = ActivitiEngine("http://localhost:8080/activiti-rest")
        self.service = Service(engine, "service")
        self.url = "http://localhost:8080/activiti-rest/service/test"
        self.dict_object = json.loads(self.get_json_object())

    def get_json_object(self):
        json_object = """{
   "id":"objectId",
   "name":"Object name",
   "type":"Other field"
}"""
        return json_object

    def should_create_objects(self):

        mock_post = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        self.service.session.post = mock_post

        self.service.create(self.dict_object, "test")

        calls = mock_post.call_args
        assert calls[0][0] == self.url
        assert json.loads(calls[1]["data"]) == self.dict_object

    def should_raise_exception_when_missing_id(self):
        mock_post = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        self.service.session.post = mock_post

        with pytest.raises(MissingID):
            self.service.create(self.dict_object, "test")

    def should_update_object(self):
        mock_response = Mock(status_code=200)
        mock_put = Mock(return_value=mock_response)
        self.service.session.put = mock_put

        self.service.update(self.dict_object, "test")

        call = mock_put.call_args
        assert call[0][0] == self.url
        assert json.loads(call[1]["data"]) == self.dict_object

    def should_raise_exception_when_unexisting_update(self):
        mock_put = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_put.return_value = mock_response
        self.service.session.put = mock_put

        with pytest.raises(NotFound):
            self.service.update(self.dict_object, "test")

    def should_raise_exception_when_simultaneous_update(self):
        mock_put = Mock()
        mock_response = Mock()
        mock_response.status_code = 409
        mock_put.return_value = mock_response
        self.service.session.put = mock_put

        with pytest.raises(UpdatedSimultaneous):
            self.service.update(self.dict_object, "test")

    def should_load_a_object(self):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = self.dict_object
        mock_get = Mock(return_value=mock_response)
        self.service.session.get = mock_get

        dict_object = self.service.load("test")

        mock_get.assert_called_with(self.url)
        assert dict_object == self.dict_object

    def should_raise_exception_when_loading_unexisting_object(self):
        mock_response = Mock(status_code=404)
        mock_get = Mock(return_value=mock_response)
        self.service.session.get = mock_get

        with pytest.raises(NotFound):
            self.service.load("test")

    def should_delete_a_object(self):
        mock_response = Mock(status_code=204)
        mock_del = Mock(return_value=mock_response)
        self.service.session.delete = mock_del

        self.service.delete("test")

        mock_del.assert_called_with(self.url)

    def should_raise_exception_when_deleting_unexisting_object(self):
        mock_response = Mock(status_code=404)
        mock_del = Mock(return_value=mock_response)
        self.service.session.delete = mock_del

        with pytest.raises(NotFound):
            self.service.delete("test")

    def should_post_with_json(self):
        pass


class A_Variables_class:

    def setup_method(self, method):

        rest_variables = """[
                      {
                        "name" : "doubleTaskVar",
                        "scope" : "local",
                        "type" : "double",
                        "value" : 99.99
                      },
                      {
                        "name" : "stringProcVar",
                        "scope" : "global",
                        "type" : "string",
                        "value" : "This is a ProcVariable"
                      }
                    ]"""
        self.rest_variables = json.loads(rest_variables)
        self.variables = Variables(rest_data=self.rest_variables)

    def should_load_rest_data(self):
        assert hasattr(self.variables, "rest_data")

        # Local variables has a underscore at end of variable name
        assert self.variables["doubleTaskVar_"] == 99.99
        assert self.variables["stringProcVar"] == "This is a ProcVariable"
        assert len(self.variables) == 2
        assert self.rest_variables == self.variables.rest_data

    def should_get_rest_representation_of_differences(self):

        self.variables["newVariable"] = "content"
        self.variables["localVariable_"] = 123

        rest_result = self.variables.sync_rest()
        assert len(rest_result) == 2
        for variable in rest_result:
            if variable["name"] == "newVariable":
                assert variable["scope"] == "global"
            else:
                assert variable["scope"] == "local"
                assert variable["name"] == "localVariable"

