from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OrigUserAdmin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

import csv

import datetime

from .models import Category, Brand, Product, Address, Cart, Order


def export_to_csv(modeladmin, request, queryset):
    """ функция для экспорта выборки данных в csv"""
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts)
    print(response['Content-Disposition'])
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Записываем первую строку с заголовками полей.
    writer.writerow([field.verbose_name for field in fields])
    # Записываем данные.
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


# def order_pdf(obj):
#     return mark_safe('<a href="{}">PDF</a>'.format(
#         reverse('orders:admin_order_pdf', args=[obj.id])))


# order_pdf.short_description = 'Invoice'
export_to_csv.short_description = 'Export to CSV'


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


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "city", "street_name", "street_type", "house", "contact_phone", "contact_fio")
    list_filter = ("customer", "city")
    search_fields = ("city", "street_name", "street_type", "house")
    save_on_top = True
    save_as = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "address", "price", "paid")
    list_filter = ("customer", "paid")
    actions = [export_to_csv]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "quantity", "product", "order")
    list_filter = ("customer",)
    search_fields = ("product__name",)
