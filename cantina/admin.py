from django.contrib import admin

from . import models


class ComponentAdmin(admin.ModelAdmin):
    fields = ["item", "ingredient", "amount"]

    def get_readonly_fields(self, request, object=None):
        return ["item"] if object else []


admin.site.register(models.Customer)
admin.site.register(models.MenuItemCategory)
admin.site.register(models.MenuItem)
admin.site.register(models.InventoryItemCategory)
admin.site.register(models.InventoryItem)
admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.Tab)
admin.site.register(models.Purchase)
