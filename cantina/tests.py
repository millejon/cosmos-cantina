from django.test import TestCase

from . import models


def create_customer(
    last_name: str, planet: str, first_name: str = None, uba: str = None
) -> models.Customer:
    """Create a customer."""
    return models.Customer.objects.create(
        last_name=last_name, first_name=first_name, planet=planet, uba=uba
    )


def create_menu_item(name: str, category: str, price: int) -> models.MenuItem:
    """Create a menu item for use in purchases."""
    category = models.MenuItemCategory.objects.create(name=category)
    return models.MenuItem.objects.create(name=name, category=category, price=price)


def create_tab(customer: models.Customer) -> models.Tab:
    """Create a tab assigned to the customer passed."""
    return models.Tab.objects.create(customer=customer)


def make_purchase(
    tab: models.Tab, item: models.MenuItem, quantity: int, amount: int
) -> models.Purchase:
    """Create a purchase assigned to the tab passed."""
    return models.Purchase.objects.create(
        tab=tab, item=item, quantity=quantity, amount=amount
    )


class CustomerTestCase(TestCase):
    def setUp(self):
        create_customer(
            last_name="Radd",
            first_name="Norrin",
            planet="Zenn-La",
            uba="OHCMSZ9QF928JZNS4H20IKXP",
        )
        create_customer(last_name="Galactus", first_name="", planet="Galan", uba="")

    def test_customer_names(self):
        """
        The name attribute of the Customer model should return the
        customer's full name, whether the customer has a first name or
        not.
        """
        silver_surfer = models.Customer.objects.get(last_name="Radd")
        galactus = models.Customer.objects.get(last_name="Galactus")

        self.assertEqual(silver_surfer.name, "Norrin Radd")
        self.assertEqual(galactus.name, "Galactus")


class TabTestCase(TestCase):
    def setUp(self):
        customer = create_customer(
            last_name="Thanos", first_name="", planet="Titan", uba=""
        )
        self.tab = create_tab(customer=customer)
        self.item = create_menu_item(name="Duff Beer", category="Beer", price=5)

    def test_tab_get_purchases_with_single_purchase(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with a single
        purchase should return 1.
        """
        make_purchase(tab=self.tab, item=self.item, quantity=2, amount=10)

        self.assertEqual(len(self.tab.get_purchases()), 1)

    def test_tab_get_purchases_with_multiple_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with five
        purchases should return 5.
        """
        for _ in range(5):
            make_purchase(tab=self.tab, item=self.item, quantity=2, amount=10)

        self.assertEqual(len(self.tab.get_purchases()), 5)

    def test_tab_get_purchases_with_no_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with no purchases
        should return 0.
        """
        self.assertEqual(len(self.tab.get_purchases()), 0)

    def test_tab_get_amount_with_single_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        make_purchase(tab=self.tab, item=self.item, quantity=3, amount=15)

        self.assertEqual(self.tab.get_amount(), 15)

    def test_tab_get_amount_with_multiple_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        for _ in range(5):
            make_purchase(tab=self.tab, item=self.item, quantity=4, amount=20)

        self.assertEqual(self.tab.get_amount(), 100)

    def test_tab_get_amount_with_no_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab. A tab with no
        purchases should return 0.
        """
        self.assertEqual(self.tab.get_amount(), 0)

    def test_tab_get_amount_with_comped_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab. The amount of a tab
        after a purchase is comped should be updated accordingly.
        """
        for _ in range(5):
            make_purchase(tab=self.tab, item=self.item, quantity=2, amount=10)

        self.assertEqual(self.tab.get_amount(), 50)

        purchase = self.tab.purchase_set.all()[0]
        purchase.comp()
        purchase.save()

        self.assertEqual(self.tab.get_amount(), 40)


class PurchaseTestCase(TestCase):
    def setUp(self):
        customer = create_customer(
            last_name="Quill", first_name="Peter", planet="Earth", uba=""
        )
        tab = create_tab(customer=customer)
        item = create_menu_item(name="Duff Beer", category="Beer", price=5)
        self.purchase = make_purchase(tab=tab, item=item, quantity=2, amount=10)

    def test_purchase_update_amount_with_change_to_quantity(self):
        """
        The update_amount method of the Purchase model should update
        the amount of the purchase according to changes in quantity.
        """
        self.assertEqual(self.purchase.amount, 10)

        self.purchase.quantity = 4  # Original quantity was 2.
        self.purchase.update_amount()

        self.assertEqual(self.purchase.amount, 20)

    def test_purchase_update_amount_with_no_changes(self):
        """
        The update_amount method of the Purchase model should update
        the amount of the purchase according to changes in quantity. If
        nothing has changed, then the amount should not be affected.
        """
        self.assertEqual(self.purchase.amount, 10)

        self.purchase.update_amount()

        self.assertEqual(self.purchase.amount, 10)

    def test_purchase_comp(self):
        """
        The comp method of the Purchase model should update the amount
        of the purchase to 0.
        """
        self.assertEqual(self.purchase.amount, 10)

        self.purchase.comp()

        self.assertEqual(self.purchase.amount, 0)
