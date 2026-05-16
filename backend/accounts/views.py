from django.contrib.auth import get_user_model, login, logout
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AdminUserSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from .tasks import send_welcome_email
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_welcome_email.delay(user.pk)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Nieprawidłowe dane logowania."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Wylogowano pomyślnie."})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Hasło zostało zmienione."})


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("-created_at")
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.utils import timezone
        from django.db.models import Sum, Count
        from orders.models import Order
        from products.models import Product
        from contact.models import ContactMessage

        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        order_qs = Order.objects.all()
        order_status_counts = dict(
            order_qs.values_list("status").annotate(cnt=Count("id")).values_list("status", "cnt")
        )
        revenue = order_qs.filter(status="completed").aggregate(total=Sum("total"))["total"] or 0

        return Response({
            "users": {
                "total": User.objects.count(),
                "active": User.objects.filter(is_active=True).count(),
                "staff": User.objects.filter(is_staff=True).count(),
                "new_30d": User.objects.filter(created_at__gte=thirty_days_ago).count(),
            },
            "orders": {
                "total": order_qs.count(),
                "new_30d": order_qs.filter(created_at__gte=thirty_days_ago).count(),
                "by_status": order_status_counts,
                "revenue_completed": str(revenue),
            },
            "products": {
                "total": Product.objects.count(),
                "active": Product.objects.filter(is_active=True).count(),
                "inactive": Product.objects.filter(is_active=False).count(),
            },
            "messages": {
                "total": ContactMessage.objects.count(),
                "unread": ContactMessage.objects.filter(is_read=False).count(),
            },
        })
