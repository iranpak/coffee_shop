from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from shop.models import Product, OrderStatus, Order
from users.models import User


class ProductTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='admin1234', email='admin@g.com')
        self.customer = User.objects.create_user(username='customer', password='customer1234', email='customer@g.com')

        login_url = reverse('login')
        admin_login_data = {'username': self.admin.username, 'password': 'admin1234'}
        customer_login_data = {'username': self.customer.username, 'password': 'customer1234'}
        admin_login_response = self.client.post(login_url, admin_login_data, format='json')
        customer_login_response = self.client.post(login_url, customer_login_data, format='json')
        self.assertEqual(admin_login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', admin_login_response.data)
        self.assertEqual(customer_login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', customer_login_response.data)
        self.admin_token = 'Bearer ' + admin_login_response.data['access']
        self.customer_token = 'Bearer ' + customer_login_response.data['access']

    def test_product(self):
        url = reverse('shop:products-list')
        data1 = {}
        data2 = {'name': 'p1', 'price': 1}
        response1 = self.client.post(url, data1, format='json', HTTP_AUTHORIZATION=self.admin_token)
        response2 = self.client.post(url, data2, format='json', HTTP_AUTHORIZATION=self.admin_token)
        response3 = self.client.get(url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().name, 'p1')
        self.assertEqual(response3.data['count'], 1)

    def test_order(self):
        url = reverse('shop:orders-list')
        product1 = Product.objects.create(name='p1', price=1)
        product2 = Product.objects.create(name='p2', price=2)
        data1 = {'products': [product1.id, product2.id], 'customer': self.customer.id}
        response1 = self.client.post(url, data1, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['status'], OrderStatus.WAITING)

        detail_url = reverse('shop:orders-detail', args=[response1.data['id']])
        response2 = self.client.get(url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(response2.data['count'], 1)
        self.assertEqual(response2.data['results'][0]['total_price'], product1.price + product2.price)
        self.assertEqual(response2.data['results'][0]['customer']['username'], self.customer.username)

        data2 = {'status': OrderStatus.PREPARATION}
        response3 = self.client.patch(detail_url, data2, format='json', HTTP_AUTHORIZATION=self.admin_token)
        response4 = self.client.patch(detail_url, data2, format='json', HTTP_AUTHORIZATION=self.customer_token)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data['status'], OrderStatus.PREPARATION)
        self.assertEqual(response4.status_code, status.HTTP_403_FORBIDDEN)

        data3 = {'products': [product1.id]}
        change_url = reverse('shop:orders-detail', args=[response1.data['id']]) + 'change/'
        response5 = self.client.patch(change_url, data3, format='json', HTTP_AUTHORIZATION=self.customer_token)
        self.assertEqual(response5.status_code, status.HTTP_200_OK)
        self.assertEqual(response5.data, 'Your order is not waiting and can not be changed!')

        order = Order.objects.get(id=response2.data['results'][0]['id'])
        order.status = OrderStatus.WAITING
        order.save()
        response6 = self.client.patch(change_url, data3, format='json', HTTP_AUTHORIZATION=self.customer_token)
        self.assertEqual(response6.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response6.data['products']), 1)
        self.assertEqual(response6.data['products'][0], product1.id)

        cancel_url = reverse('shop:orders-detail', args=[response1.data['id']]) + 'cancel/'

        order.status = OrderStatus.WAITING
        order.save()
        response8 = self.client.get(cancel_url, format='json', HTTP_AUTHORIZATION=self.customer_token)
        self.assertEqual(response8.status_code, status.HTTP_200_OK)
        self.assertEqual(response8.data['status'], OrderStatus.CANCELLED)

        response7 = self.client.get(cancel_url, format='json', HTTP_AUTHORIZATION=self.customer_token)
        self.assertEqual(response7.status_code, status.HTTP_200_OK)
        self.assertEqual(response7.data, 'Your order is not waiting and can not be cancelled!')