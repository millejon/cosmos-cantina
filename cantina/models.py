from django.db import models
from django.utils import timezone


def a_week_from_now():
    """Add 7 days to the current point in time."""
    return timezone.now() + timezone.timedelta(days=7)


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
    cost = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = ["drink", "ingredient"]
        ordering = ["drink", "-amount"]

    def __str__(self):
        return f"{self.drink.name} - {self.ingredient.name}"


class Tab(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    opened = models.DateTimeField(default=timezone.now)
    due = models.DateTimeField(default=a_week_from_now)
    closed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["customer", "opened"]
        ordering = ["-closed", "customer__last_name"]

    def __str__(self):
        return f"{self.customer.last_name}: {self.opened}"


class Purchase(models.Model):
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ["tab", "time"]
        ordering = ["-time"]

    def __str__(self):
        return f"{self.tab.customer.last_name}: {self.drink.name}"
