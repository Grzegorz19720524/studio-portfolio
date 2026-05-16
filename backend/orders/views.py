from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        if user.is_staff:
            return qs.all()
        return qs.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "set_status":
            return OrderStatusSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ("destroy", "set_status"):
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Brak uprawnień."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)
