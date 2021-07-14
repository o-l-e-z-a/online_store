from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *


urlpatterns = format_suffix_patterns([
    path("addresses/", AddressModelViewSet.as_view({'get': 'list'})),
    path("address/<int:pk>/", AddressModelViewSet.as_view({'get': 'retrieve'})),
    path("address/add/", AddressModelViewSet.as_view({'post': 'create'})),
    path("address/<int:pk>/update/", AddressModelViewSet.as_view({'post': 'partial_update'})),
    path('address/<int:pk>/delete/', AddressModelViewSet.as_view({'delete': 'destroy'})),
    path('categories/', CategoryLIstViewSet.as_view({'get': 'list'})),
    path('category/<int:pk>', ProductForCategoryViewSet.as_view({'get': 'list'})),
    path('product/<int:pk>/', ProductDetailViewSet.as_view({'get': 'retrieve'})),
    path('product/<int:pk>/add/', CartModelViewSet.as_view({'post': 'create'})),
    path('search/', SearchView.as_view({'get': 'list'})),
    path('cart/', CartModelViewSet.as_view({'get': 'list'})),
    path('cart/<int:pk>/update/', CartModelViewSet.as_view({'post': 'partial_update'})),
    path('cart/<int:pk>/delete/', CartModelViewSet.as_view({'delete': 'destroy'})),
    path('short-cart/', ShortCartModelViewSet.as_view({'get': 'list'})),
])

