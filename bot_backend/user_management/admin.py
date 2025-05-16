from django.contrib import admin

from .models import User, TgUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)
    list_filter = ("is_staff", "is_active")
    list_editable = ("is_staff", "is_active")


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "tg_first_name", "tg_last_name", "tg_username", "is_bot", "created_at", "updated_at",
                    "is_active")
    search_fields = ("tg_id", "tg_first_name", "tg_last_name", "tg_username", "is_bot", "created_at", "updated_at")
    ordering = ("created_at",)
    list_filter = ("is_bot", "created_at", "updated_at", "is_active")
