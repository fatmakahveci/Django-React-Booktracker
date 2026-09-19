from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Django's auth forms hash new passwords and keep stored hashes read-only.
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("email", "user_name", "is_staff", "email_verified", "date_joined")
    search_fields = ("email", "user_name")
    ordering = ("email",)
    readonly_fields = ("date_joined", "last_login", "session_version")

    fieldsets = (
        (None, {"fields": ("email", "user_name", "password", "email_verified")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Sessions", {"fields": ("session_version",)}),
        ("Important dates", {"fields": ("date_joined", "last_login")}),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "user_name", "password1", "password2")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "email_verified")}),
    )
