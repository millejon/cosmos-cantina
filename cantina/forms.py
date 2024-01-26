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
        fields = ["item", "ingredient", "amount"]


class PurchaseForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=models.Customer.objects.all())

    class Meta:
        model = models.Purchase
        fields = ["customer", "item", "quantity"]


class TabForm(forms.ModelForm):
    class Meta:
        model = models.Tab
        fields = ["customer", "due", "closed"]
        widgets = {
            "due": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "closed": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
