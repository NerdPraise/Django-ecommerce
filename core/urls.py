# Django Modules
from django.urls import path

# Local modules
from .views import (
    CheckoutView, HomeView, ItemDetailView, OrderSummaryiew, PaymentView,
    add_to_cart, remove_from_cart, remove_single_item_from_cart
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

    # ++++++++++++++++++++++++ PRODUCT +++++++++++++++++++++++
    path("checkout", CheckoutView.as_view(), name="checkout-page"),
    path("product/<slug>", ItemDetailView.as_view(), name="product"),
    path("add-to-cart/<slug>", add_to_cart, name="add-to-cart"),
    path("remove-from-cart/<slug>", remove_from_cart, name="remove_from_cart"),
    path("remove-single-from-cart/<slug>", remove_single_item_from_cart,
         name="remove_single_item_from_cart"),
    path("order-summary", OrderSummaryiew.as_view(), name="order_summary"),
    path("payment/<payment_option>", PaymentView.as_view(), name="payment"),
]
