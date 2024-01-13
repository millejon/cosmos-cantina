from django.contrib import admin

from . import models

admin.site.register(models.Customer)
admin.site.register(models.DrinkCategory)
admin.site.register(models.Drink)
admin.site.register(models.IngredientCategory)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
admin.site.register(models.Tab)
admin.site.register(models.Purchase)
