from django import forms

from . import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ["last_name", "first_name", "planet", "uba"]


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = models.MenuItem
        fields = ["category", "name", "price"]


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = models.InventoryItem
        fields = [
            "category",
            "name",
            "cost",
            "stock",
            "reorder_point",
            "reorder_amount",
        ]


class ComponentForm(forms.ModelForm):
    class Meta:
        model = models.Component
        fields = ["ingredient", "amount"]


class PurchaseForm(forms.ModelForm):
    customer_choices = (
        (customer.id, f"{customer.first_name} {customer.last_name}")
        for customer in models.Customer.objects.all()
    )
    customer = forms.ChoiceField(choices=customer_choices)

    class Meta:
        model = models.Purchase
        fields = ["drink", "customer", "quantity"]


class TabForm(forms.ModelForm):
    class Meta:
        model = models.Tab
        fields = ["customer", "due", "closed"]
        widgets = {
            "due": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "closed": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
