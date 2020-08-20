# Django Imports
from django.contrib import admin

# Local imports
from .models import BillingAddress, Coupons, Item, OrderItem, Order, Payment


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("item", "ordered")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "ordered")


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(Coupons)
