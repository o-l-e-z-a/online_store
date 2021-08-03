import debug_toolbar

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('shop.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('payment/', include('payment.urls')),
    path('coupons/', include('coupons.urls')),
]

urlpatterns += doc_urls

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

