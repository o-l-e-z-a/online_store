from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from .views import AddressModelViewSet, CartModelViewSet, CategoryLIstViewSet, ProductDetailViewSet, \
    ProductForCategoryViewSet, SearchView, ShortCartModelViewSet, OrderViewSet



urlpatterns = format_suffix_patterns([
    path("addresses/", AddressModelViewSet.as_view({'get': 'list'}), name='addresses_list'),
    path("address/<int:pk>/", AddressModelViewSet.as_view({'get': 'retrieve'}), name='address_detail'),
    path("address/add/", AddressModelViewSet.as_view({'post': 'create'}), name='address_add'),
    path("address/<int:pk>/update/", AddressModelViewSet.as_view({'post': 'partial_update'}), name='address_update'),
    path('address/<int:pk>/delete/', AddressModelViewSet.as_view({'delete': 'destroy'}), name='address_delete'),
    path('categories/', CategoryLIstViewSet.as_view({'get': 'list'}), name='categories_list'),
    path('category/<int:pk>', ProductForCategoryViewSet.as_view({'get': 'list'}), name='product_for_category'),
    path('product/<int:pk>/add/', CartModelViewSet.as_view({'post': 'create'}), name='product_add_to_cart'),
    path('product/<int:pk>/', ProductDetailViewSet.as_view({'get': 'retrieve'}), name='product_detail'),
    path('search/', SearchView.as_view({'get': 'list'}), name='search'),
    path('cart/', CartModelViewSet.as_view({'get': 'list'}), name='cart_list'),
    path('cart/<int:pk>/update/', CartModelViewSet.as_view({'post': 'partial_update'}), name='cart_update'),
    path('cart/<int:pk>/delete/', CartModelViewSet.as_view({'delete': 'destroy'}), name='cart_delete'),
    path('short-cart/', ShortCartModelViewSet.as_view({'get': 'list'}), name='short_cart'),
    path('order/<int:pk>/', OrderViewSet.as_view({'get': 'retrieve'}), name='order_detail'),
    path('orders/', OrderViewSet.as_view({'get': 'list'}), name='order_list'),
    path('order/add/', OrderViewSet.as_view({'post': 'create'}), name='order_add'),
    # path('admin/order/<int:order_id>/pdf/', admin_order_pdf, name='admin_order_pdf'),
])



