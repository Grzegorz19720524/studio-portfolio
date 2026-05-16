from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ContactMessage
from .serializers import (
    ContactMessageSerializer,
    ContactMessageCreateSerializer,
    ContactMessageMarkReadSerializer,
)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.order_by("-created_at")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return ContactMessageCreateSerializer
        if self.action == "mark_read":
            return ContactMessageMarkReadSerializer
        return ContactMessageSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        from .tasks import send_contact_confirmation, notify_admins_new_contact
        serializer = ContactMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = serializer.save()
        send_contact_confirmation.delay(msg.pk)
        notify_admins_new_contact.delay(msg.pk)
        return Response(
            {"detail": "Wiadomość została wysłana."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["patch"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        serializer = ContactMessageMarkReadSerializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ContactMessageSerializer(message).data)
