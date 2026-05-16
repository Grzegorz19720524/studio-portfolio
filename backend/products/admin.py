from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    @admin.display(description="Liczba produktów")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "category")
    list_editable = ("price", "is_active")
    search_fields = ("name", "description", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "description")}),
        ("Cena i dostępność", {"fields": ("price", "is_active")}),
        ("Daty", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["activate_products", "deactivate_products"]

    @admin.action(description="Aktywuj wybrane produkty")
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Aktywowano {updated} produktów.")

    @admin.action(description="Dezaktywuj wybrane produkty")
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Dezaktywowano {updated} produktów.")
