from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "user_name", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff")}),
        ("Important dates", {"fields": ("date_joined",)}),
    )

    add_fieldsets = (
        (None, {"fields": ("user_name", "email", "password", "match_password")}),
        ("Permissions", {"fields": ("is_active", "is_staff")}),
        ("Important dates", {"fields": ("date_joined",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
