from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import UserProfile
from ninja_extra.testing import TestAsyncClient
from main.api import api

class UserTests(TestCase):
    def setUp(self):
        self.client = TestAsyncClient(api)
        self.register_url = reverse('api:register')
        self.login_url = reverse('api:login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, json=self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(response.json()['username'], self.user_data['username'])

    def test_login_user(self):
        # First, register the user
        self.client.post(self.register_url, json=self.user_data)
        
        # Then, attempt to log in
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertIn('role', response.json())

    def test_login_invalid_credentials(self):
        login_data = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, json=login_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid credentials')

    def test_register_user_missing_fields(self):
        incomplete_user_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_url, json=incomplete_user_data)
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity

    def test_register_user_duplicate_username(self):
        self.client.post(self.register_url, json=self.user_data)
        response = self.client.post(self.register_url, json=self.user_data)
        self.assertEqual(response.status_code, 400)  # Bad Request

    def test_login_user_inactive(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = False
        user.save()
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, json=login_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid credentials')