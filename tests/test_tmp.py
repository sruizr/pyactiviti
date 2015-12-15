from requests_mock import mock
from unittest.mock import patch
import pytest


@pytest.fixture
def mock_request():
    return mock()


class A_test:
    def should_mock(self, mock_request):
        pass
