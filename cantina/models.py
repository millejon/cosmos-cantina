from django.db import models
from django.utils import timezone
import datetime
import decimal


def a_week_from_now() -> datetime.datetime:
    """Add 7 days to the current point in time."""
    return timezone.now() + timezone.timedelta(days=7)


class Customer(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Leave blank if customer has only one name.",
    )
    planet = models.CharField(max_length=100)
    uba = models.CharField("UBA Number", max_length=24, blank=True)

    class Meta:
        unique_together = ["last_name", "first_name", "uba"]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self) -> str:
        """
        Return customer's full name. If customer has only one name,
        then only it will be returned.
        """
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.last_name}"


class MenuItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Menu categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(MenuItemCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name


class InventoryItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Inventory categories"

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(InventoryItemCategory, on_delete=models.CASCADE)
    stock = models.DecimalField(max_digits=10, decimal_places=2, help_text="bottles")
    cost = models.DecimalField(max_digits=6, decimal_places=2, help_text="per bottle")
    reorder_point = models.IntegerField(help_text="bottles")
    reorder_amount = models.IntegerField(help_text="bottles")

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name


class Component(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=4, decimal_places=2, help_text="ounces")

    class Meta:
        unique_together = ["item", "ingredient"]
        ordering = ["item", "ingredient__name"]

    def __str__(self):
        return f"{self.item.name} - {self.ingredient.name}"


class Tab(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    due = models.DateTimeField(default=a_week_from_now)
    closed = models.DateTimeField(null=True, blank=True)
    opened = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-closed", "customer__last_name"]

    def __str__(self):
        if not self.closed:
            return f"{self.customer.first_name} {self.customer.last_name}"
        else:
            return f"{self.customer.first_name} {self.customer.last_name} [{self.closed.strftime('%Y-%m-%d %H:%M')}]"

    def get_purchases(self) -> models.query.QuerySet:
        """
        Return all purchases associated with the tab in chronological
        order.
        """
        return self.purchase_set.all().order_by("time")

    def get_amount(self) -> decimal.Decimal:
        """
        Return total price of all purchases made on the tab. If zero
        purchases were made, an amount of 0 is returned.
        """
        if self.purchase_set.all():
            return self.purchase_set.aggregate(models.Sum("amount"))["amount__sum"]
        else:
            return decimal.Decimal(0)


class Purchase(models.Model):
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=40, decimal_places=2, default=0)

    class Meta:
        ordering = ["-time"]

    def __str__(self):
        return f"{self.tab.customer.last_name}: {self.item.name} x {self.quantity}"

    def update_amount(self) -> None:
        """
        Update amount of purchase according to the cost of the menu
        item and the quantity of the item purchased.
        """
        self.amount = self.item.price * self.quantity

    def comp(self) -> None:
        """
        Set amount of purchase to 0.
        """
        self.amount = 0
