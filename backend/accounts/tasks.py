from celery import shared_task
from studio.email import send_email, render_email


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        if not user.email:
            return
        body = render_email("welcome.txt", {"username": user.username})
        send_email(
            subject="Witaj w Studio!",
            message=body,
            recipient_list=[user.email],
        )
    except User.DoesNotExist:
        return
    except Exception as exc:
        raise self.retry(exc=exc)
