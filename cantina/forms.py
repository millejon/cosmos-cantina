from django import forms

from . import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ["first_name", "last_name", "planet", "uba"]


class PurchaseForm(forms.ModelForm):
    customer_choices = (
        (customer.id, f"{customer.first_name} {customer.last_name}")
        for customer in models.Customer.objects.all()
    )
    customer = forms.ChoiceField(choices=customer_choices)

    class Meta:
        model = models.Purchase
        fields = ["customer", "drink", "quantity"]
