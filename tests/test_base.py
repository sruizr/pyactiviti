from pyactiviti.base import (
                             JavaDictMapper,
                             Service,
                             Query,
                             MissingID,
                             NotFound,
                             UpdatedSimultaneous,

                             )
from pyactiviti.process_engine import ActivitiEngine

from unittest.mock import Mock, patch
import json
import pdb
import pytest


class A_Service:

    def setup_method(self, method):
        engine = ActivitiEngine("http://localhost:8080/activiti-rest")
        self.service = Service(engine)
        self.url = "http://test/url"
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

        self.service.create(self.url, self.dict_object)

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
            self.service.create(self.url, self.dict_object)

    def should_update_object(self):
        mock_response = Mock(status_code=200)
        mock_put = Mock(return_value=mock_response)
        self.service.session.put = mock_put

        self.service.update(self.url, self.dict_object)

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
            self.service.update(self.url, self.dict_object)

    def should_raise_exception_when_simultaneous_update(self):
        mock_put = Mock()
        mock_response = Mock()
        mock_response.status_code = 409
        mock_put.return_value = mock_response
        self.service.session.put = mock_put

        with pytest.raises(UpdatedSimultaneous):
            self.service.update(self.url, self.dict_object)

    def should_load_a_object(self):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = self.dict_object
        mock_get = Mock(return_value=mock_response)
        self.service.session.get = mock_get

        dict_object = self.service.load(self.url)

        mock_get.assert_called_with(self.url)
        assert dict_object == self.dict_object
