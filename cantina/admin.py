from django.contrib import admin

from . import models

admin.site.register(models.Customer)
admin.site.register(models.Drink)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
