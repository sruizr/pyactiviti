import pdb
import pytest


class TestQuery:

    def test_parameter(self, parameter_method, parameter_name, value):

        query = parameter_method(value)
        assert query.parameters[parameter_name] == value
        query.parameters.pop(parameter_name)

    def test_parameter_with_like(self, parameter_method, parameter_name,
                                 value):
        self.test_parameter(parameter_method, parameter_name, value)
        self.test_parameter(parameter_method, parameter_name+"Like",
                            value+"%")

    def test_parameter_object(self, parameter_method, parameter_name, obj):
        query = parameter_method(obj)
        assert query.parameters[parameter_name] == obj.id
        query.parameters.pop(parameter_name)

    def test_parameter_numerical(self, parameter_method, parameter_name,
                                 operator, value):
        query = parameter_method(value, operator)
        assert query.parameters[parameter_name] == value
        query.parameters.pop(parameter_name)


class TestService:
    def test_exception(self, mock, mock_exception, expected_exception):
        pass


def test_transfer_exception(raised_exception, expected_exception, mock,
                            method, *args, **wargs):
    mock.side_effect = raised_exception
    try:
        method(*args, **wargs)
        pytest.fail(expected_exception.__name__ +
                    " should be fired")
    except expected_exception:
        pass
