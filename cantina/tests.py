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
        customer = models.Customer.objects.create(last_name="Thanos", planet="Titan")
        models.Tab.objects.create(customer=customer)
        category = models.MenuItemCategory.objects.create(name="Beer")
        models.MenuItem.objects.create(name="Duff Beer", category=category, price=5)

    def make_purchase(self, tab: models.Tab) -> None:
        """Create a Purchase object assigned to the tab passed."""
        models.Purchase.objects.create(
            tab=tab,
            item=models.MenuItem.objects.get(name="Duff Beer"),
            quantity=2,
            amount=10,
        )

    def test_tab_get_purchases_with_single_purchase(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with a single
        purchase should return 1.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )
        self.make_purchase(tab)

        self.assertEqual(len(tab.get_purchases()), 1)

    def test_tab_get_purchases_with_multiple_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with five
        purchases should return 5.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )
        for _ in range(5):
            self.make_purchase(tab)

        self.assertEqual(len(tab.get_purchases()), 5)

    def test_tab_get_purchases_with_no_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with no purchases
        should return 0.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )

        self.assertEqual(len(tab.get_purchases()), 0)

    def test_tab_get_amount_with_single_purchase(self):
        """
        The get_amount methods of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )
        self.make_purchase(tab)

        self.assertEqual(tab.get_amount(), 10)

    def test_tab_get_amount_with_multiple_purchase(self):
        """
        The get_amount methods of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )
        for _ in range(5):
            self.make_purchase(tab)

        self.assertEqual(tab.get_amount(), 50)

    def test_tab_get_amount_with_no_purchase(self):
        """
        The get_amount methods of the Tab model should return the total
        price of all purchases assigned to the tab. A tab with no
        purchases should return 0.
        """
        tab = models.Tab.objects.get(
            customer=models.Customer.objects.get(last_name="Thanos")
        )

        self.assertEqual(tab.get_amount(), 0)
