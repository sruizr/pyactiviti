from requests_mock import mock
from unittest.mock import patch
import pytest

import responses
import requests


@pytest.fixture
def mock_request():
    return mock()


class A_test:

    @responses.activate
    def should_test_one(self):
        responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                      json={"error": "not found"}, status=404)

        responses.add(responses)

        resp = requests.get('http://twitter.com/api/1/foobar')
        assert resp.json() == {"error": "not found"}

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://twitter.com/api/1/foobar'
        assert responses.calls[0].response.text == '{"error": "not found"}'
