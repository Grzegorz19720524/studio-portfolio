from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "company", "phone", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name", "company", "phone")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_login", "date_joined")
    list_editable = ("is_active",)

    fieldsets = UserAdmin.fieldsets + (
        ("Dane kontaktowe", {"fields": ("phone", "company")}),
        ("Daty", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Dane kontaktowe", {"fields": ("email", "first_name", "last_name", "phone", "company")}),
    )

    actions = ["activate_users", "deactivate_users"]

    @admin.action(description="Aktywuj wybranych użytkowników")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Aktywowano {updated} użytkowników.")

    @admin.action(description="Dezaktywuj wybranych użytkowników")
    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f"Dezaktywowano {updated} użytkowników.")
