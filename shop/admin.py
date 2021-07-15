from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OrigUserAdmin

from .models import Category, Brand, Product, Address, User, Cart


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brand", "description", "price")
    list_filter = ("category", "brand")
    search_fields = ("name", "brand__name", "category__name")
    save_on_top = True
    save_as = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "sort_order", "url")
    list_filter = ("parent",)
    search_fields = ("name", "parent__name")
    save_on_top = True
    save_as = True
    prepopulated_fields = {"url": ("name",)}


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "quantity", "product")
    list_filter = ("customer", "product")
    search_fields = ("product__name", )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "city", "street_name", "street_type", "house", "contact_phone", "contact_fio")
    list_filter = ("customer", "city")
    search_fields = ("city", "street_name", "street_type", "house")
    save_on_top = True
    save_as = True


@admin.register(User)
class UserAdmin(OrigUserAdmin):
    list_display = ("id", "telephone", "date_birthday", "first_name", "last_name", "email", "is_staff", "is_superuser")
    save_on_top = True
    save_as = True
