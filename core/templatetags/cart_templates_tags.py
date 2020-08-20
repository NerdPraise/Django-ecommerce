# Django Modules
from django import template

# Local Modules
from core.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            order_count = qs[0].items.count()
            return order_count
        return 0