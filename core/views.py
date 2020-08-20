# Future

# Standard Library

# Third parties

# Django imports
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Local imports
from .models import BillingAddress, Item, OrderItem, Order
from .forms import CheckoutForm

# Try Else statements


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            "form": form
        }
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data['street_address']
                apartment_address = form.cleaned_data['apartment_address']
                country = form.cleaned_data['country']
                zip_code = form.cleaned_data['zip_code']
                # TODO: add functionality later
                # same_billing_address = form.cleaned_data['same_billing_address']
                # save_info = form.cleaned_data['save_info']
                payment_options = form.cleaned_data["payment_options"]
                billing_address = BillingAddress(
                    user=self.request.user,
                    zip_code=zip_code,
                    street_address=street_address,
                    country=country,
                    apartment_address=apartment_address
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                print("valid")
                print(form.cleaned_data)
                # TODO: Add payment mode
                return redirect("core:checkout-page")
            print(form.errors)
            messages.warning(self.request, form.errors)
            return redirect("core:checkout-page")
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an order")
            return redirect("core:order_summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # Code block for GET request
        return render(self.request, "payment.html")

    def post(self, *args, **kwargs):
        # Code block for POST request
        pass


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class OrderSummaryiew(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order
            }
            return render(self.request, "order_summary.html", context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, ordered=False, user=request.user)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    ordered_date = timezone.now()
    if order_qs.exists():
        # check if the order_item is in the order
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, "This item quantity has been updated")
            return redirect("core:order_summary")
        else:
            order.items.add(order_item)
            messages.success(
                request, "This item quantity was added to your cart")
        # return redirect("core:product",slug=slug)

    else:
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item quantity was added to your cart")
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = Item.objects.get(slug=slug)
    order_item = OrderItem.objects.get(
        item=item, ordered=False, user=request.user)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order.items.remove(order_item)
            messages.success(
                request, "This item quantity was removed from your cart")
            # return redirect("core:product", slug=slug)
        else:
            # alert that user doesn't have that order item
            messages.warning(request, "This item is not in your cart")
            # return redirect("core:product", slug=slug)
    else:
        # alert that user doesn't have an order
        messages.info(request, "You don't have an order yet")
    return redirect("core:order_summary")


@login_required
def remove_single_item_from_cart(request, slug):
    item = Item.objects.get(slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, ordered=False, user=request.user)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.success(
                request, "This item quantity was removed from your cart")

        else:
            # alert that user doesn't have that order item
            messages.warning(request, "This item is not in your cart")
    else:
        # alert that user doesn't have an order
        messages.info(request, "You don't have an order yet")
    return redirect("core:order_summary")
