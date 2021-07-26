from django.db.models import F, DecimalField, ExpressionWrapper, Sum
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import permissions, filters
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from .serializers import (
    AddressReadUpdateDeleteSerializer,
    AddressAddSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductForCategoryListSerializer,
    CartReadSerializer,
    CartCreateUpdateSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
)
from .service import PaginationProductForCategory, PaginationSearch, product_search, get_product_sum, \
    get_products_total_sum
from .models import Address, Category, Product, Cart, Order
from .tasks import cart_created


class AddressModelViewSet(ModelViewSet):
    """ CRUD адреса пользователя """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AddressAddSerializer
        else:
            return AddressReadUpdateDeleteSerializer

    def get_queryset(self):
        return Address.objects.filter(customer=self.request.user.pk).select_related('customer')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class CategoryLIstViewSet(ListModelMixin, GenericViewSet):
    """ Вывод списка категорий """
    queryset = Category.objects.all().prefetch_related('children').order_by('-sort_order')
    serializer_class = CategorySerializer


class ProductDetailViewSet(RetrieveModelMixin, GenericViewSet):
    """ Просмотр отдельного товара """
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all().select_related('brand').prefetch_related('category')


class ProductForCategoryViewSet(ListModelMixin, GenericViewSet):
    """ Просмотр всех товаров, принадлежащих к отдельной категории"""
    serializer_class = ProductForCategoryListSerializer
    pagination_class = PaginationProductForCategory
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['id', 'name', 'price']
    ordering = ['id']

    def get_queryset(self):
        return Product.objects.select_related('brand').prefetch_related('category').filter(category__id=self.kwargs['pk'])


class SearchView(ListModelMixin, GenericViewSet):
    """ Поиск по товарам """
    serializer_class = ProductDetailSerializer
    pagination_class = PaginationSearch

    def get_queryset(self):
        query_params = self.request.query_params.get('search', None)
        results = product_search(query_params)
        return results


class CartModelViewSet(ModelViewSet):
    """ CRUD корзины """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return CartCreateUpdateSerializer
        else:
            return CartReadSerializer

    def get_queryset(self):
        return get_product_sum(self.request.user)

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        cart_created.delay(self.kwargs['pk'])
        serializer.save(customer=self.request.user, product=product)


class ShortCartModelViewSet(ViewSet):
    """ Краткая корзина """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = get_products_total_sum(self.request.user)
        return Response({
            'final_cost': queryset['final_cost'],
            'count': queryset['count']
        })


class OrderViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).select_related('address', 'customer').\
            prefetch_related('items', 'items__product')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        else:
            return OrderDetailSerializer

    def perform_create(self, serializer):
        total_sum = get_products_total_sum(self.request.user)['final_cost']
        serializer.save(customer=self.request.user, price=total_sum)


