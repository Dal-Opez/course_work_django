from django.core.mail import send_mail
from django.utils import timezone
from .models import MailingAttempt


def send_mailing(mailing):
    clients = mailing.client.all()

    for client in clients:
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.letter_body,
                from_email=None,
                recipient_list=[client.email],
                fail_silently=False
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.SUCCESS,
                server_response=f"Успешно отправлено на {client.email}",
                owner=mailing.owner
                # date_attempt теперь заполняется автоматически
            )

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.FAIL,
                server_response=f"Ошибка для {client.email}: {str(e)}",
                owner=mailing.owner
                # date_attempt теперь заполняется автоматически
            )