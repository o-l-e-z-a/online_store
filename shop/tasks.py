from django.core.mail import send_mail

from online_store.celery import app

from .models import User

from online_store.locale_settings import EMAIL_HOST_USER


@app.task
def order_created(order_id, user_id):
    """Отправление email-уведомления при успешном оформлении заказа"""
    user = User.objects.get(pk=user_id)
    subject = 'Ваш  заказ №{}'.format(order_id)
    message = 'Дорогой {}, {} \n\n Вы успешно сделали свой заказ.\
    Номер вашего заказа {}.'.format(user.first_name, user.last_name, order_id)
    mail_sent = send_mail(subject,
                          message,
                          EMAIL_HOST_USER,
                          [EMAIL_HOST_USER],
                          fail_silently=False)
    return mail_sent
