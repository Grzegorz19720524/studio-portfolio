from celery import shared_task
from django.conf import settings
from studio.email import send_email, render_email


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation(self, order_id):
    from .models import Order
    try:
        order = Order.objects.select_related("user").prefetch_related("items__product").get(pk=order_id)
        if not order.user or not order.user.email:
            return
        body = render_email("order_confirmation.txt", {"order": order})
        send_email(
            subject=f"Potwierdzenie zamówienia #{order.id}",
            message=body,
            recipient_list=[order.user.email],
        )
    except Order.DoesNotExist:
        return
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_status_changed(self, order_id):
    from .models import Order
    try:
        order = Order.objects.select_related("user").get(pk=order_id)
        if not order.user or not order.user.email:
            return
        body = render_email("order_status_changed.txt", {"order": order})
        send_email(
            subject=f"Zmiana statusu zamówienia #{order.id}",
            message=body,
            recipient_list=[order.user.email],
        )
    except Order.DoesNotExist:
        return
    except Exception as exc:
        raise self.retry(exc=exc)
