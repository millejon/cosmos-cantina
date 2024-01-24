from django.test import TestCase

from . import models


class CustomerTestCase(TestCase):
    def setUp(self):
        models.Customer.objects.create(
            last_name="Radd",
            first_name="Norrin",
            planet="Zenn-La",
            uba="OHCMSZ9QF928JZNS4H20IKXP",
        )
        models.Customer.objects.create(last_name="Galactus", planet="Galan")

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
        self.customer = models.Customer.objects.create(
            last_name="Thanos", planet="Titan"
        )
        self.tab = models.Tab.objects.create(customer=self.customer)
        category = models.MenuItemCategory.objects.create(name="Beer")
        self.beer = models.MenuItem.objects.create(
            name="Duff Beer", category=category, price=5
        )

    def make_purchase(self) -> None:
        """Create a Purchase object."""
        models.Purchase.objects.create(
            tab=self.tab,
            item=self.beer,
            quantity=2,
            amount=10,
        )

    def test_tab_get_purchases_with_single_purchase(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with a single
        purchase should return 1.
        """
        self.make_purchase()

        self.assertEqual(len(self.tab.get_purchases()), 1)

    def test_tab_get_purchases_with_multiple_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with five
        purchases should return 5.
        """
        for _ in range(5):
            self.make_purchase()

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
        self.make_purchase()

        self.assertEqual(self.tab.get_amount(), 10)

    def test_tab_get_amount_with_multiple_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        for _ in range(5):
            self.make_purchase()

        self.assertEqual(self.tab.get_amount(), 50)

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
            self.make_purchase()

        self.assertEqual(self.tab.get_amount(), 50)

        purchase = self.tab.purchase_set.all()[0]
        purchase.comp()
        purchase.save()

        self.assertEqual(self.tab.get_amount(), 40)


class PurchaseTestCase(TestCase):
    def setUp(self):
        customer = models.Customer.objects.create(last_name="Thanos", planet="Titan")
        tab = models.Tab.objects.create(customer=customer)
        category = models.MenuItemCategory.objects.create(name="Beer")
        self.item = models.MenuItem.objects.create(
            name="Duff Beer", category=category, price=5
        )
        self.purchase = models.Purchase.objects.create(
            tab=tab, item=self.item, quantity=2, amount=10
        )

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
