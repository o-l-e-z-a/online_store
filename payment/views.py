import braintree

from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from shop.models import Order


class Token(APIView):
    """ получение токена для оплаты"""

    def get(self, request):
        token = braintree.ClientToken.generate()
        return Response({'token': token}, status=200)


class Checkout(APIView):
    """ Оплата заказа"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        received_json_data = request.data
        nonce_from_the_client = received_json_data.get("payment_method_nonce",
                                                    "none")
        print(nonce_from_the_client)
        result = braintree.Transaction.sale({
            "amount": order.price,
            "credit_card": {
                "number": "5105105105105100",
                "expiration_date": "05/2011",
                "cvv": "123"
            },
            "options": {
                "submit_for_settlement": True
            }
        })

        if result.is_success or result.transaction:
            order.paid = True
            # Сохранение ID транзакции в заказе
            order.braintree_id = result.transaction.id
            order.save()
            return Response({'message': 'good'}, status=200)
        else:
            return Response({'message': 'error in transaction'}, status=400)
