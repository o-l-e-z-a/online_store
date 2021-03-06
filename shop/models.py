from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.conf import settings

from coupons.models import Coupon


class Address(models.Model):
    """
        Модель адреса пользователя
    """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Покупатель', on_delete=models.CASCADE)
    city = models.CharField('Город', max_length=32)
    street_name = models.CharField('Название улицы', max_length=64)
    street_type = models.CharField('Тип города', max_length=16)
    house = models.CharField('Дом', max_length=64)
    contact_phone = models.CharField('Контактный телефон', max_length=32, null=True)
    contact_fio = models.CharField('ФИО', max_length=64, null=True)

    def __str__(self):
        return f'Город {self.city}, улица {self.street_name}, дом {self.house}'

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class Category(models.Model):
    """
        Модель категорий
    """
    parent = models.ForeignKey(
        'self', verbose_name='Родитель', on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    name = models.CharField('Название', max_length=255)
    sort_order = models.IntegerField('Порядок сортировки', default=0)
    url = models.SlugField('Url', max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}, родитель: {self.parent}'

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.url})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ('-sort_order', )


class Brand(models.Model):
    """
        Модель бренда
    """
    name = models.CharField('Название', max_length=255)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"


class Product(models.Model):
    """
        Модель товаров магазина
    """
    name = models.CharField('Название', max_length=255)
    brand = models.ForeignKey(Brand, verbose_name='Бренд', on_delete=models.CASCADE, null=True)
    description = models.TextField('Описание', null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2)
    category = models.ManyToManyField(Category, verbose_name='Категории', related_name='products')

    def __str__(self):
        return f'{self.name} {self.brand} , {self.category}'

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Cart(models.Model):
    """
        Модель корзины
    """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Покупатель', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество')
    order = models.ForeignKey(
        'Order', verbose_name='Заказ', on_delete=models.CASCADE, related_name='items', null=True, blank=True
    )

    def __str__(self):
        return f'{self.customer}, {self.product.name} : {self.quantity}'

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Order(models.Model):
    """
        Модель заказа
    """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Покупатель', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name='Адрес', on_delete=models.CASCADE)
    price = models.DecimalField('Стоимость', max_digits=12, decimal_places=2)
    date_add = models.DateTimeField('Дата заказа', auto_now_add=True)
    braintree_id = models.CharField(max_length=150, blank=True)
    paid = models.BooleanField('Оплата', default=False)
    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return f'{self.id} {self.price} {self.paid}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

