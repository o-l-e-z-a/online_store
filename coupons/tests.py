from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from shop.models import Brand, Cart, Category, Product, Address, User, Order

from .models import Coupon

from datetime import timedelta

class CouponTest(APITestCase):

    def setUp(self) -> None:

        user_test1 = User.objects.create_user(
            email='test1@test1.ru', password="testPassword1", first_name='test1', last_name='test1', telephone='test1'
        )
        user_test1.save()

        brand1 = Brand.objects.create(name='6 соток')
        brand1.save()

        category1 = Category.objects.create(name='Овощи', sort_order=3, url='ovoshi')
        category1.save()

        product1 = Product.objects.create(
            name='Огерец "6 соток" свежий', brand=brand1, price=Decimal('35')
        )
        product1.category.add(category1)
        product1.save()

        address1 = Address.objects.create(
            customer=user_test1, street_type='test', street_name='test', city='test', house='test'
        )
        address1.save()

        cart = Cart.objects.create(customer=user_test1, product=product1, quantity=2)
        cart.save()

        self.order = Order.objects.create(customer=user_test1, address=address1, price=product1.price*2)
        self.order.save()

        self.coupon = Coupon.objects.create(
            code='TEST_CODE',
            valid_from=timezone.now() - timedelta(1),
            valid_to=timezone.now() + timedelta(2),
            discount=20,
            active=True,
        )

    def test_accept_coupon(self):
        response = self.client.post(reverse('apply'), {'code': 'TEST_CODE'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_coupon(self):
        response = self.client.post(reverse('apply'), {'code': 'dsfdsfsdfsdfsd'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

