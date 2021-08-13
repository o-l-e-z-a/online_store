from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OrigUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(OrigUserAdmin):
    list_display = ("id", "telephone", "date_birthday", "first_name", "last_name", "email", "is_staff", "is_superuser")
    save_on_top = True
    save_as = True
