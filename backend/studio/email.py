from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_email(subject, message, recipient_list, html_message=None):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def render_email(template_name, context):
    return render_to_string(f"emails/{template_name}", context)
