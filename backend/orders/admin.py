from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("unit_price", "subtotal")
    fields = ("product", "quantity", "unit_price", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "item_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "user__username", "notes")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("total", "created_at", "updated_at")
    inlines = [OrderItemInline]

    fieldsets = (
        (None, {"fields": ("user", "status", "notes")}),
        ("Kwota", {"fields": ("total",)}),
        ("Daty", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = [
        "mark_confirmed",
        "mark_in_progress",
        "mark_completed",
        "mark_cancelled",
    ]

    @admin.display(description="Pozycji")
    def item_count(self, obj):
        return obj.items.count()

    @admin.action(description="Oznacz jako: Potwierdzone")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status=Order.Status.CONFIRMED)
        self.message_user(request, f"Potwierdzono {updated} zamówień.")

    @admin.action(description="Oznacz jako: W realizacji")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=Order.Status.IN_PROGRESS)
        self.message_user(request, f"Ustawiono 'W realizacji' dla {updated} zamówień.")

    @admin.action(description="Oznacz jako: Zrealizowane")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status=Order.Status.COMPLETED)
        self.message_user(request, f"Zrealizowano {updated} zamówień.")

    @admin.action(description="Oznacz jako: Anulowane")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Order.Status.CANCELLED)
        self.message_user(request, f"Anulowano {updated} zamówień.")
