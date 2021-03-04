from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='admin1234', email='admin@g.com')

        login_url = reverse('login')
        admin_login_data = {'username': self.admin.username, 'password': 'admin1234'}
        admin_login_response = self.client.post(login_url, admin_login_data, format='json')
        self.assertEqual(admin_login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', admin_login_response.data)
        self.admin_token = 'Bearer ' + admin_login_response.data['access']

    def test_crete_user(self):
        url = reverse('users:users-list')
        data = {'username': 'customer', 'email': 'customer@g.com', 'password': 'customer1234'}
        response1 = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        data.update({'first_name': 'ali', 'last_name': 'alavi'})
        response2 = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user(self):
        customer = User.objects.create_user(username='customer', password='customer1234', email='customer@g.com')

        login_url = reverse('login')
        login_data = {'username': 'customer', 'password': 'new_password'}
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)

        update_url = reverse('users:users-detail', args=[customer.id])
        update_data = {'password': 'new_password'}
        update_response = self.client.patch(update_url, update_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
