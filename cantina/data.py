from . import forms, models

objects = {
    "customers": {
        "model": models.Customer,
        "form": forms.CustomerForm,
    },
    "menu": {
        "model": models.MenuItem,
        "categories": models.MenuItemCategory,
        "form": forms.MenuItemForm,
    },
    "inventory": {
        "model": models.InventoryItem,
        "categories": models.InventoryItemCategory,
        "form": forms.InventoryItemForm,
    },
    "components": {
        "model": models.Component,
        "form": forms.ComponentForm,
    },
    "tabs": {
        "model": models.Tab,
        "form": forms.TabForm,
    },
    "purchases": {
        "model": models.Purchase,
        "form": forms.PurchaseForm,
    },
}
