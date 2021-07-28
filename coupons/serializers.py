from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """ Сериализатор для регистрации """
    code = serializers.CharField(max_length=50)

    class Meta:
        model = Coupon
        fields = ('code', )
