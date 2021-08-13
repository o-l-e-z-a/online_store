from rest_framework import status
from rest_framework.test import APITestCase


class UserProfileTests(APITestCase):

    def test_registration(self):
        response = self.client.post(r'http://127.0.0.1:8000/auth/users/', {
            'email': 'test5@test5.ru',
            'password': "testPassword1",
            'first_name': 'test5',
            'last_name': 'test5',
            'telephone': 'test5'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_login_registration(self):
        response = self.client.post(r'http://127.0.0.1:8000/auth/users/', {
            'email': 'test1@test1ru',
            'password': "testPassword1",
            'first_name': 'test5',
            'last_name': 'test5',
            'telephone': 'test5'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
