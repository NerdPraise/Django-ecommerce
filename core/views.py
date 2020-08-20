# Future

# Standard Library

# Third parties
import stripe

# Django imports
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Local imports
from .models import BillingAddress, Item, OrderItem, Order, Payment
from .forms import CheckoutForm

# Try Else statements


stripe.api_key = settings.STRIPE_SECRET_KEY


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
            order = Order.objects.get(user=self.request.user, ordered=False)
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

                # TODO: Add payment mode
                if payment_options == "S":
                    return redirect("core:payment", payment_option="stripe")
                elif payment_options == "P":
                    return redirect("core:payment", payment_option="paypal")
                else:
                    messages.error(self.request, "Invalid payment option")
                    return redirect("core:checkout")
            else:
                # if form is not valid
                print(form.errors)
                messages.warning(self.request, form.errors)
                return redirect("core:checkout-page")
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an order")
            return redirect("core:order_summary")


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        payment_option = kwargs["payment_option"]
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            "order": order,
            "payment_option": payment_option
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get("stripeToken")
        amount = order.get_total() * 100

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=int(amount),
                currency="usd",
                source=token,
            )

            # create payment
            payment = Payment.objects.create(
                user=self.request.user,
                stripe_charge_id=charge["id"],
                amount=amount
            )
            # Change order items ordered status
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            # Assign payment to order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your Order was successful")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be
            messages.error(self.request, f"{e.error.message}")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"{e.error.message}")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, f"{e.error.message}")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, f"{e.error.message}")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, f"{e.error.message}")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, f"{e.error.message}")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, f"{e.error.message}")
        finally:
            return redirect("/")


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
