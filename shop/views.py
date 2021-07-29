from django.shortcuts import get_object_or_404

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
    OrderReadSerializer,
    OrderCreateSerializer,
)
from .service import PaginationProductForCategory, PaginationSearch, product_search, get_product_sum, \
    get_products_total_sum, get_sale
from .models import Address, Category, Product, Order

from coupons.models import Coupon

# from django.conf import settings
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# import cairosvg
# import weasyprint


# @staff_member_required
# def admin_order_pdf(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     html = render_to_string('orders/order/pdf.html', {'order': order})
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)
#     weasyprint.HTML(string=html).write_pdf(response,stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
#     return response


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
        return Product.objects.select_related('brand').prefetch_related('category').filter(
            category__id=self.kwargs['pk'])


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
        serializer.save(customer=self.request.user, product=product)


class ShortCartModelViewSet(ViewSet):
    """ Просмтор краткой информации о  корзине """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = get_products_total_sum(self.request.user)
        return Response({
            'final_cost': queryset['final_cost'],
            'count': queryset['count']
        })


class OrderViewSet(ModelViewSet):
    """
    Просмотр и добавление заказа
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).select_related('address', 'customer'). \
            prefetch_related('items', 'items__product')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        else:
            return OrderReadSerializer

    def perform_create(self, serializer):
        total_sum = get_products_total_sum(self.request.user)['final_cost']
        coupon_id = self.request.session.get('coupon_id')
        try:
            coupon = Coupon.objects.get(pk=coupon_id)
        except Coupon.DoesNotExist:
            serializer.save(customer=self.request.user, price=total_sum)
        else:
            sale = get_sale(coupon, total_sum)
            final_price = total_sum - sale
            serializer.save(customer=self.request.user, price=final_price, coupon=coupon, discount=coupon.discount)

        order_id = serializer.data.get('id')
        self.request.session['order_id'] = order_id
