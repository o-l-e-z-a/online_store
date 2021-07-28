from django.urls import path
from .views import CouponApply

urlpatterns = [
    path('apply/', CouponApply.as_view(), name='apply'),
]
