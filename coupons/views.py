from django.utils import timezone
from rest_framework import status

from .models import Coupon
from rest_framework.views import APIView
from .serializers import CouponSerializer
from rest_framework.response import Response


class CouponApply(APIView):
    """  Обработка ввода  скидочного купона """

    def post(self, request):
        now = timezone.now()
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
                request.session['coupon_id'] = coupon.id
                return Response({'message': 'accept coupon'}, status=status.HTTP_200_OK)
            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
        return Response({'message': 'coupon does not exist'}, status=status.HTTP_404_NOT_FOUND)

