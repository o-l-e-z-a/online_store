from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from online_store.celery import app

from django.conf import settings

from online_store.settings import EMAIL_HOST_USER

User = get_user_model()

@app.task
def order_created(order_id, user_id):
    """Отправление email-уведомления при успешном оформлении заказа"""
    user = settings.AUTH_USER_MODEL.objects.get(pk=user_id)
    subject = 'Ваш  заказ №{}'.format(order_id)
    message = 'Дорогой {}, {} \n\n Вы успешно сделали свой заказ.\
    Номер вашего заказа {}.'.format(user.first_name, user.last_name, order_id)
    mail_sent = send_mail(subject,
                          message,
                          EMAIL_HOST_USER,
                          [EMAIL_HOST_USER],
                          fail_silently=False)
    return mail_sent
