from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("name", "email", "subject", "message", "created_at")

    fieldsets = (
        ("Nadawca", {"fields": ("name", "email")}),
        ("Treść", {"fields": ("subject", "message")}),
        ("Status", {"fields": ("is_read", "created_at")}),
    )

    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description="Oznacz jako przeczytane")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Oznaczono {updated} wiadomości jako przeczytane.")

    @admin.action(description="Oznacz jako nieprzeczytane")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"Oznaczono {updated} wiadomości jako nieprzeczytane.")

    def has_add_permission(self, request):
        return False
