from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from studio.email import send_email, render_email


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_confirmation(self, message_id):
    from .models import ContactMessage
    try:
        msg = ContactMessage.objects.get(pk=message_id)
        body = render_email("contact_confirmation.txt", {
            "name": msg.name,
            "subject": msg.subject,
            "message": msg.message,
        })
        send_email(
            subject="Otrzymaliśmy Twoją wiadomość",
            message=body,
            recipient_list=[msg.email],
        )
    except ContactMessage.DoesNotExist:
        return
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_admins_new_contact(self, message_id):
    from .models import ContactMessage
    User = get_user_model()
    try:
        msg = ContactMessage.objects.get(pk=message_id)
        admin_emails = list(
            User.objects.filter(is_staff=True, is_active=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )
        if not admin_emails:
            return
        body = render_email("contact_admin_notification.txt", {
            "name": msg.name,
            "email": msg.email,
            "subject": msg.subject,
            "message": msg.message,
        })
        send_email(
            subject=f"Nowa wiadomość od {msg.name}: {msg.subject}",
            message=body,
            recipient_list=admin_emails,
        )
    except ContactMessage.DoesNotExist:
        return
    except Exception as exc:
        raise self.retry(exc=exc)
