from django.urls import path

from .views import Checkout, Token

app_name = 'payment'

urlpatterns = [
    path('process/', Checkout.as_view(), name='process'),
    path('token/', Token.as_view())
]
