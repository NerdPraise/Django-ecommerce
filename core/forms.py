# Django imports
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),

)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "1234 Main St"
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Apartment or suite"
        }))
    country = CountryField(blank_label="Select Country").formfield(widget=CountrySelectWidget(attrs={
        "class": "custom-select d-block w-100 form-control"
    }))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)
