from django.contrib import admin

from . import models


class RecipeAdmin(admin.ModelAdmin):
    fields = ["drink", "ingredient", "amount"]

    def get_readonly_fields(self, request, object=None):
        return ["drink"] if object else []


admin.site.register(models.Customer)
admin.site.register(models.DrinkCategory)
admin.site.register(models.Drink)
admin.site.register(models.IngredientCategory)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Tab)
admin.site.register(models.Purchase)
