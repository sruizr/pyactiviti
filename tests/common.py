import unittest
from pyactiviti.base import RestConnection

ACTIVITI_AUTH = ('kermit', 'kermit')
ACTIVITI_SERVICE = 'http://localhost:8080/activiti-rest'

rest_connection = RestConnection(ACTIVITI_SERVICE, auth=ACTIVITI_AUTH)
