from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "subtotal"]

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Produkt jest niedostępny.")
        return value


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Produkt jest niedostępny.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "user_email", "status", "status_display",
            "notes", "total", "items", "created_at", "updated_at",
        ]
        read_only_fields = ["total", "created_at", "updated_at", "user"]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ["notes", "items"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Zamówienie musi zawierać co najmniej jeden produkt.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context.get("request")
        order = Order.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            **validated_data,
        )
        for item in items_data:
            product = item["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                unit_price=product.price,
            )
        order.recalculate_total()
        return order


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        allowed = [s.value for s in Order.Status]
        if value not in allowed:
            raise serializers.ValidationError(f"Nieprawidłowy status. Dozwolone: {allowed}")
        return value
