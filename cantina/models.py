from django.db import models


class Customer(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True)
    planet = models.CharField(max_length=100)
    uba = models.CharField("UBA Number", max_length=24, blank=True)

    class Meta:
        unique_together = ["last_name", "first_name"]
        ordering = ["last_name"]

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.last_name


class Drink(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    stock = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
