from decimal import Decimal

from rest_framework import serializers

from .models import Category, User, Product, Address, Cart, Order
from .recommender import Recommender
from .tasks import order_created

from djoser.serializers import UserCreateSerializer


class RegistrationSerializer(UserCreateSerializer):
    """ Сериализатор для регистрации """

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'telephone', 'first_name', 'last_name', 'date_birthday', 'password')


class AddressReadUpdateDeleteSerializer(serializers.ModelSerializer):
    """ Сериализатор для удаления, обновления,просмотра адреса """
    class Meta:
        model = Address
        exclude = ['id', 'customer']


class AddressAddSerializer(serializers.ModelSerializer):
    """ Сериализатор для создание адреса """

    class Meta:
        model = Address
        exclude = ['id', 'customer']

    def create(self, validated_data):
        user = User.objects.get(pk=validated_data.get('customer').pk)
        if not validated_data.get('contact_fio'):
            contact_fio = user.last_name + ' ' + user.first_name
            validated_data.update(contact_fio=contact_fio)
        if not validated_data.get('contact_phone'):
            contact_phone = user.telephone
            validated_data.update(contact_phone=contact_phone)
        return Address.objects.create(**validated_data)


class FilterCategoryListSerializer(serializers.ListSerializer):
    """ Фильтр категорий, только родители """
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """ Вывод рекурсивно потомков """
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода категорий """
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterCategoryListSerializer
        model = Category
        fields = ("id", "name", "url", "sort_order", "parent", "children")


class CategoryListSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра краткой информации о категориях"""
    class Meta:
        model = Category
        fields = ("name", )


class ProductForCategoryListSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра товаров по категориям"""

    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


class ProductDetailSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра отдельных товаров"""
    category = CategoryListSerializer(read_only=True, many=True)
    brand = serializers.SlugRelatedField(slug_field='name', read_only=True)
    recommended = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'category', 'brand', 'name', 'description', 'price', 'recommended')

    def get_recommended(self, obj):
        """ получение рекомендуемых товаров"""
        r = Recommender()
        recommended_products = r.suggest_products_for([obj, Product.objects.get(pk=355299)], 4)
        serializer = ProductForCategoryListSerializer(recommended_products, many=True)
        return serializer.data


class CartCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления коризны"""
    quantity = serializers.IntegerField(required=False)

    class Meta:
        model = Cart
        fields = ('quantity',)

    def create(self, validated_data):
        """ добавление товара"""
        cart = Cart.objects.filter(
            customer=validated_data.get('customer'), product=validated_data.get('product'), order__isnull=True
        ).first()
        if cart:
            cart.quantity += 1
            cart.save()
            return cart
        else:
            # cart_created.delay(cart.id)
            validated_data.update(quantity=1)
            return Cart.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """ обновление кол-во товара """
        quantity = validated_data.get('quantity', 0)
        if quantity > 0:
            instance.quantity = quantity
            instance.save()
        elif quantity == 0:
            instance.delete()
        return instance


class CartReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода корзины"""
    product = ProductForCategoryListSerializer(read_only=True)
    sum = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Cart
        fields = ('id', 'product', 'quantity', 'sum', 'order')


class OrderCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания заказа"""

    class Meta:
        model = Order
        exclude = ['price', 'customer']

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        r = Recommender()
        products = []
        for cart in Cart.objects.select_related('product', 'customer').filter(
                customer=validated_data.get('customer'), order__isnull=True
        ):
            products.append(cart.product)
            cart.order = order
            cart.save()
        user_id = order.customer.pk
        order_created.delay(order.pk, user_id)
        r.products_bought(products)
        return order


class OrderCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра заказанных товаров"""
    sum = serializers.SerializerMethodField()
    product = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Cart
        fields = ('product', 'quantity', 'sum')

    def get_sum(self, obj):
        total_sum = obj.quantity * obj.product.price
        return total_sum - total_sum * obj.order.discount / Decimal('100')


class OrderReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра заказа"""
    address = AddressReadUpdateDeleteSerializer(read_only=True)
    items = OrderCartSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'address', 'items', 'discount', 'price', 'paid')

