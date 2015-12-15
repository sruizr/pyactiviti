# -*- coding: utf-8 -*-
import json
from requests.status_codes import codes
import requests_mock
from . import common as c
from pyactiviti.user import User

from pyactiviti import exceptions
import pytest


@pytest.fixture
def mock_request():
    return requests_mock.mock()


class A_User:

    def setup_method(self, method):
        self.user_name = "user1"
        self.user = User(self.user_name)
        self.user.rest_connection = c.rest_connection

    @pytest.mark.current
    def should_confirm_if_not_exists(self, mock_request):
        mock_request.get(
            User.get_by_id('user1'),
            status_code=codes.not_found
        )

        self.assertFalse(self.user.exists())

    def should_confirm_if_exists(self, mock):
        mock_request.get(
            self.activiti.user_url('user1'),
            status_code=codes.ok
        )

        self.assertTrue(self.user.exists())

    def test_get_user(self, mock_request):
        user_id = 'user1'
        fake_user = self.fake_user(user_id)
        mock_request.get(
            self.activiti.user_url(user_id),
            json=fake_user,
            status_code=codes.ok
        )
        remote_user = self.activiti.get_user(user_id)
        self.assertEqual(fake_user, remote_user)

    def fake_user(self, login):
        return {
            'id': login,
            'firstName': 'firstName',
            'lastName': 'lastName',
            'url': self.activiti.user_url(login)
        }

    def test_users(self, mock_request):
        fake_users = {
            'total': 2,
            'size': 2,
            'sort': 'id',
            'order': 'asc',
            'data': [
                self.fake_user(u'user1'),
                self.fake_user(u'user2'),
            ]
        }

        mock_request.get(
            self.activiti.users_url(),
            headers={'Content-Type': 'application/json'},
            status_code=codes.ok, json=fake_users
        )

        result = self.activiti.users()['data']
        self.assertEqual(len(result), len(fake_users['data']))
        self.assertEqual(result, fake_users['data'])

    def test_create_user(self, mock_request):
        fake_user = self.fake_user('user1')
        mock_request.post(
            self.activiti.users_url(),
            json=fake_user,
            status_code=codes.created,
        )

        user = self.activiti.create_user('user1', 'foo@bar.org', 'secret')

        self.assertEqual(user, fake_user)

    def test_create_user_conflict(self, mock_request):
        mock_request.post(
            self.activiti.users_url(),
            status_code=codes.conflict,
            json={'exception': 'Exception'}
        )

        with self.assertRaises(exceptions.UserAlreadyExists):
            self.activiti.create_user('user1', 'foo@bar.org', 'secret')

    @requests_mock.mock()
    def test_create_user_missing_id(self, mock_request):
        mock_request.post(
            self.activiti.users_url(),
            status_code=codes.bad_request,
        )
        with self.assertRaises(exceptions.UserMissingID):
            self.activiti.create_user(None, 'foo@bar.org', 'secret')

    def test_delete_user(self, mock_request):
        mock_request.delete(
            self.activiti.user_url('user1'),
            status_code=codes.no_content,
        )
        self.assertTrue(self.activiti.delete_user('user1'))

    def test_delete_user_not_found(self, mock):
        mock_request.delete(
            self.activiti.user_url('user1'),
            status_code=codes.not_found
        )
        with self.assertRaises(exceptions.UserNotFound):
            self.activiti.delete_user('user1')

    def test_update_user(self, mock):
        update = {
            'firstName': 'Tijs',
            'lastName': 'Barrez',
            'email': 'no-reply@alfresco.org',
            'password': 'pass123',
        }

        mock.put(
            self.activiti.user_url('user1'),
            status_code=codes.ok,
            json=update,
        )

        response = self.activiti.user_update('user1', update)
        self.assertDictEqual(response, update)

    def test_update_user_not_found(self, mock):
        mock.put(
            self.activiti.user_url('user1'),
            status_code=codes.not_found,
        )
        with self.assertRaises(exceptions.UserNotFound):
            self.activiti.user_update('user1', {})

    def test_update_user_updated_simultaneous(self, mock):
        mock.put(
            self.activiti.user_url('user1'),
            status_code=codes.conflict
        )
        with self.assertRaises(exceptions.UserUpdatedSimultaneous):
            self.activiti.user_update('user1', {})
