from datetime import timedelta

from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from coupons.models import Coupon
from .models import Brand, Cart, Category, Product, Address, User, Order


class ShopTests(APITestCase):

    def setUp(self) -> None:
        brand1 = Brand.objects.create(name='6 соток')
        brand1.save()
        brand2 = Brand.objects.create(name='Красная цена')
        brand2.save()

        user_test1 = User.objects.create_user(
            email='test1@test1.ru', password="testPassword1", first_name='test1', last_name='test1', telephone='test1'
        )
        user_test1.save()
        user_test2 = User.objects.create_user(
            email='test2@test2.ru', password="testPassword2", first_name='test2', last_name='test2', telephone='test2'
        )
        user_test2.save()

        self.user_test1_token = Token.objects.create(user=user_test1)
        self.user_test2_token = Token.objects.create(user=user_test2)

        category1 = Category.objects.create(name='Овощи', sort_order=3, url='ovoshi')
        category1.save()
        category2 = Category.objects.create(name='Огурец', sort_order=10, url='ogurez', parent=category1)
        category2.save()
        category3 = Category.objects.create(
            name='Огурец карликовый', sort_order=5, url='ogurez_karlikovii', parent=category2
        )
        category3.save()
        self.category4 = Category.objects.create(name='Помидор', sort_order=9, url='pomidor', parent=category1)
        self.category4.save()

        self.product1 = Product.objects.create(
            name='Огерец "6 соток" свежий', brand=brand1, price=Decimal('35')
        )
        self.product1.category.add(category3)
        self.product1.save()

        self.product2 = Product.objects.create(
            name='Помидор "Красная цена" скидка 5%', brand=brand2, price=Decimal('45')
        )
        self.product2.category.add(self.category4)
        self.product3 = Product.objects.create(
            name='Помидор "6 соток" большой', brand=brand1, price=Decimal('28')
        )
        self.product3.category.add(self.category4)

        self.address1 = Address.objects.create(
            customer=user_test1, street_type='test', street_name='test', city='test', house='test'
        )
        self.address1.save()

        self.cart = Cart.objects.create(customer=user_test1, product=self.product1, quantity=2)
        self.cart.save()

        self.order = Order.objects.create(customer=user_test1, address=self.address1, price=self.product1.price * 2)
        self.order.save()

        self.coupon = Coupon.objects.create(
            code='TEST_CODE',
            valid_from=timezone.now() - timedelta(1),
            valid_to=timezone.now() + timedelta(2),
            discount=20,
            active=True,
        )

    def test_addresses_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.get(reverse('addresses_list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_fail_addresses_list(self):
        response = self.client.get(reverse('addresses_list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_addresses_add(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('address_add'),
            {'street_type': 'test_add', 'street_name': 'test_add', 'city': 'test_add', 'house': 'test_add'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_address_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.delete(reverse('address_delete', kwargs={'pk': self.address1.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_address_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        address_pk = self.address1.pk
        response = self.client.post(
            reverse('address_update', kwargs={'pk': address_pk}),
            {'street_type': 'TEST_STREET', 'house': '23423'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        address = Address.objects.get(pk=address_pk)
        self.assertEqual(address.street_type, 'TEST_STREET')
        self.assertEqual(address.house, '23423')

    def test_failure_addresses_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('address_update', kwargs={'pk': self.address1.pk}),
            {'street_type': [1223, 123]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_addresses_add(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('address_add'),
            {'street_type': 'test_add', 'street_name': 'test_add', 'city': 'test_add'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_token_address_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test2_token.key)
        response = self.client.delete(reverse('address_delete', kwargs={'pk': self.address1.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_pk_address_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test2_token.key)
        response = self.client.delete(reverse('address_delete', kwargs={'pk': 777}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_address_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.get(reverse('address_detail', kwargs={'pk': self.address1.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {
                'city': 'test',
                'street_name': 'test',
                'street_type': 'test',
                'house': 'test',
                'contact_phone': None,
                'contact_fio': None
            },
            response.data
        )

    def test_categories_list(self):
        response = self.client.get(reverse('categories_list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['children']), 2)
        self.assertEqual(len(response.data[0]['children'][0]['children']), 1)

    def test_product_detail(self):
        response = self.client.get(reverse('product_detail', kwargs={'pk': self.product1.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((self.product1.pk, 'Огерец "6 соток" свежий'), (response.data['id'], response.data['name']))

    def test_failure_product_detail(self):
        response = self.client.get(reverse('product_detail', kwargs={'pk': 777}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_to_category(self):
        response = self.client.get(reverse('product_for_category', kwargs={'pk': self.category4.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            ('Помидор "Красная цена" скидка 5%', 'Помидор "6 соток" большой'),
            (response.data['data'][0]['name'], response.data['data'][1]['name'])
        )

    def test_failure_product_to_category(self):
        response = self.client.get(reverse('product_for_category', kwargs={'pk': 777}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_search(self):
        response_vegetables = self.client.get(reverse('search') + '?search=овощи', format='json')
        self.assertEqual(response_vegetables.status_code, status.HTTP_200_OK)
        self.assertEqual(response_vegetables.data['count'], 2)
        response_tomato = self.client.get(reverse('search') + '?search=помидор', format='json')
        self.assertEqual(response_tomato.status_code, status.HTTP_200_OK)
        self.assertEqual(response_tomato.data['count'], 2)
        response_small_cucumber = self.client.get(reverse('search') + '?search=карликовый огурец', format='json')
        self.assertEqual(response_small_cucumber.status_code, status.HTTP_200_OK)
        self.assertEqual(response_small_cucumber.data['count'], 1)

    def test_fail_search(self):
        response_vegetables = self.client.get(reverse('search') + '?search=fdbdfbdfb', format='json')
        self.assertEqual(response_vegetables.status_code, status.HTTP_200_OK)
        self.assertEqual(response_vegetables.data['count'], 0)

    def test_cart_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.get(reverse('cart_list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_add(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('product_add_to_cart',
                    kwargs={'pk': self.product2.pk}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_2 = self.client.post(
            reverse('product_add_to_cart',
                    kwargs={'pk': self.product2.pk}),
            format='json'
        )
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        cart = self.client.get(reverse('cart_list'), format='json')
        self.assertEqual(len(cart.data), 2)
        self.assertEqual(cart.json()[1].get('quantity'), 2)

    def test_cart_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.delete(reverse('cart_delete', kwargs={'pk': self.cart.pk}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cart = Cart.objects.exists()
        self.assertEqual(cart, False)

    def test_cart_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        cart_pk = self.cart.pk
        response = self.client.post(reverse('cart_update', kwargs={'pk': cart_pk}), {'quantity': 77}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart = Cart.objects.get(pk=cart_pk)
        self.assertEqual(cart.quantity, 77)

    def test_failure_cart_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        cart_pk = self.cart.pk
        response = self.client.post(reverse('cart_update', kwargs={'pk': cart_pk}), {'quantity': 'dfgdfg'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_cart(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.get(reverse('short_cart'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['final_cost'], Decimal('70.00'))

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
            'email': 'test1@test1.ru',
            'password': "testPassword1",
            'first_name': 'test5',
            'last_name': 'test5',
            'telephone': 'test5'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_order(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('order_add'),
            {'address': self.address1.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_order_with_coupon(self):
        response = self.client.post(reverse('apply'), {'code': 'TEST_CODE'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_test1_token.key)
        response = self.client.post(
            reverse('order_add'),
            {'address': self.address1.pk},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = self.client.get(reverse('order_list'), format='json')
        self.assertEqual(len(order.data), 2)
        self.assertEqual(order.json()[1].get('discount'), 20)
        self.assertEqual(Decimal(order.json()[1].get('price')), self.product1.price*2*Decimal('0.8'))

