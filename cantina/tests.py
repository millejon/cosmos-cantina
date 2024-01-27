from django.test import TestCase
from django.urls import reverse
from datetime import datetime

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


def create_tab(customer: models.Customer, closed: datetime = None) -> models.Tab:
    """Create a tab assigned to the customer passed."""
    return models.Tab.objects.create(customer=customer, closed=closed)


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
        item = create_menu_item(name="Shi'ar Sake", category="Wine", price=7)
        self.purchase = make_purchase(tab=tab, item=item, quantity=2, amount=14)

    def test_purchase_update_amount_with_change_to_quantity(self):
        """
        The update_amount method of the Purchase model should update
        the amount of the purchase according to changes in quantity.
        """
        self.assertEqual(self.purchase.amount, 14)

        self.purchase.quantity = 4  # Original quantity was 2.
        self.purchase.update_amount()

        self.assertEqual(self.purchase.amount, 28)

    def test_purchase_update_amount_with_no_changes(self):
        """
        The update_amount method of the Purchase model should update
        the amount of the purchase according to changes in quantity. If
        nothing has changed, then the amount should not be affected.
        """
        self.assertEqual(self.purchase.amount, 14)

        self.purchase.update_amount()

        self.assertEqual(self.purchase.amount, 14)

    def test_purchase_comp(self):
        """
        The comp method of the Purchase model should update the amount
        of the purchase to 0.
        """
        self.assertEqual(self.purchase.amount, 14)

        self.purchase.comp()

        self.assertEqual(self.purchase.amount, 0)


class AllCustomersViewTestCase(TestCase):
    def test_no_customers(self):
        """
        If no customers exist, an appropriate message should be
        displayed.
        """
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "customers"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/customers.html")
        self.assertContains(response, "No customers are available.")
        self.assertQuerySetEqual(response.context["instances"], [])

    def test_single_customer(self):
        """
        The customers page should display a single customer if only one
        customer is added.
        """
        captain_marvel = create_customer(
            last_name="Mar-Vell",
            first_name="",
            planet="Kree-Lar",
            uba="G66P171OPBQA90AJBT9T22HO",
        )
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "customers"})
        )
        self.assertQuerySetEqual(response.context["instances"], [captain_marvel])

    def test_multiple_customers(self):
        """
        The customers page should display multiple customers sorted by
        their last name.
        """
        gladiator = create_customer(
            last_name="Kallark",
            first_name="",
            planet="Strontia",
            uba="Y551W20W1AEMKJYRUP53THER",
        )
        beta_ray_bill = create_customer(
            last_name="Bill",
            first_name="Beta Ray",
            planet="Korbin",
            uba="KRAYCABNAU123FLNO3R77M8B",
        )
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "customers"})
        )
        self.assertQuerySetEqual(
            response.context["instances"], [beta_ray_bill, gladiator]
        )


class AllTabsViewTestCase(TestCase):
    def setUp(self):
        create_customer(
            last_name="Raccoon", first_name="Rocket", planet="Halfworld", uba=""
        )
        create_customer(last_name="Groot", first_name="", planet="Planet X", uba="")

    def test_no_tabs(self):
        """If no tabs exist, an appropriate message should be displayed."""
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "tabs"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/tabs.html")
        self.assertContains(response, "No tabs are available.")
        self.assertQuerySetEqual(response.context["instances"], [])

    def test_single_tab(self):
        """
        The tabs page should display a single tab if only one tab is
        added.
        """
        rocket_racoon = models.Customer.objects.get(last_name="Raccoon")
        tab = create_tab(customer=rocket_racoon)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "tabs"})
        )
        self.assertQuerySetEqual(response.context["instances"], [tab])

    def test_multiple_tabs(self):
        """
        The tabs page should display multiple tabs sorted by the time
        they were opened in descending order.
        """
        rocket_racoon = models.Customer.objects.get(last_name="Raccoon")
        groot = models.Customer.objects.get(last_name="Groot")
        tab1 = create_tab(customer=rocket_racoon)
        tab2 = create_tab(customer=groot)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "tabs"})
        )
        self.assertQuerySetEqual(response.context["instances"], [tab2, tab1])


class AllPurchasesViewTestCase(TestCase):
    def setUp(self):
        customer = create_customer(
            last_name="Titan", first_name="Gamora", planet="Zen-Whoberi", uba=""
        )
        self.tab = create_tab(customer=customer)
        self.item = create_menu_item(
            name="Infinity Watch", category="Cocktail", price=12
        )

    def test_no_purchases(self):
        """
        If no purchases exist, an appropriate message should be
        displayed.
        """
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "purchases"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/purchases.html")
        self.assertContains(response, "No purchases are available.")
        self.assertQuerySetEqual(response.context["instances"], [])

    def test_single_purchase(self):
        """
        The purchases page should display a single purchase if only one
        purchase is added.
        """
        purchase = make_purchase(tab=self.tab, item=self.item, quantity=1, amount=12)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "purchases"})
        )
        self.assertQuerySetEqual(response.context["instances"], [purchase])

    def test_multiple_purchases(self):
        """
        The purchases page should display multiple purchases sorted by
        the time they were made in descending order.
        """
        purchase1 = make_purchase(tab=self.tab, item=self.item, quantity=3, amount=36)
        purchase2 = make_purchase(tab=self.tab, item=self.item, quantity=2, amount=24)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "purchases"})
        )
        self.assertQuerySetEqual(response.context["instances"], [purchase2, purchase1])


class CustomerDetailsViewTestCase(TestCase):
    def test_no_customers(self):
        """
        If no customers exist, the detail view of a customer should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "customers", "id": 1})
        )
        self.assertEqual(response.status_code, 404)

    def test_customer_with_no_uba(self):
        """
        The detail view of a customer should display the customer
        information. If a customer does not have a UBA number, the
        field should not be present in the detail view of a customer.
        """
        drax = create_customer(
            last_name="Douglas", first_name="Arthur", planet="Earth", uba=""
        )
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "customers", "id": drax.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/customer.html")
        self.assertContains(response, drax.last_name)
        self.assertContains(response, drax.first_name)
        self.assertContains(response, drax.planet)
        self.assertNotContains(response, "UBA")

    def test_customer_with_uba_and_no_tabs(self):
        """
        If a customer has a UBA number, the detail view of a customer
        should also displayed it with the rest of the customer
        information. If the customer has not opened any tabs, there
        should be no 'Account History' section.
        """
        black_bolt = create_customer(
            last_name="Boltagon",
            first_name="Blackagar",
            planet="Attilan",
            uba="FWURWP48NRK1QAZUHLWX3IL0",
        )
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "customers", "id": black_bolt.id})
        )
        self.assertContains(response, "UBA")
        self.assertContains(response, black_bolt.uba)
        self.assertNotContains(response, "Account History")

    def test_customer_with_tabs(self):
        """
        If the customer has opened tabs, the detail view for the
        customer should list the closed tabs last in descending order
        of when they were closed.
        """
        medusa = create_customer(
            last_name="Amaquelin",
            first_name="Medusalith",
            planet="Attilan",
            uba="KLVREX6N766S014EN01CELID",
        )
        tab1 = create_tab(
            customer=medusa,
            closed=datetime(year=2023, month=12, day=26, hour=19, minute=20, second=14),
        )
        tab2 = create_tab(customer=medusa)
        tab3 = create_tab(
            customer=medusa,
            closed=datetime(year=2024, month=1, day=1, hour=0, minute=0, second=1),
        )
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "customers", "id": medusa.id})
        )
        self.assertContains(response, "Account History")
        self.assertQuerySetEqual(medusa.tab_set.all(), [tab2, tab3, tab1])


class TabDetailsViewTestCase(TestCase):
    def setUp(self):
        self.customer = create_customer(
            last_name="Summers",
            first_name="Gabriel",
            planet="Chandilar",
            uba="P86KIIMSJRG5AMPEPZ16A1ZO",
        )
        self.item = create_menu_item(
            name="Skrull Vineyards Pinot Noir", category="Wine", price=6
        )

    def test_no_tabs(self):
        """
        If no tabs exist, the detail view of a tab should return a 404
        status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "tabs", "id": 1})
        )
        self.assertEqual(response.status_code, 404)

    def test_open_tab_with_no_purchases(self):
        """
        The detail view of a tab should display the tab information. If
        a tab is still open, the Due field should be present and the
        Closed field should not be present in the detail view of a tab.
        If the tab has no purchases assigned to it, then an appropriate
        message should be displayed.
        """
        tab = create_tab(customer=self.customer)
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "tabs", "id": tab.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/tab.html")
        self.assertContains(response, tab.customer.name)
        self.assertContains(response, tab.opened.strftime("%Y-%m-%d %H:%M"))
        self.assertContains(response, tab.due.strftime("%Y-%m-%d %H:%M"))
        self.assertNotContains(response, "Closed")
        self.assertContains(response, "No purchases have been made.")

    def test_closed_tab_with_purchases(self):
        """
        The detail view of a tab should display the tab information. If
        a tab is closed, the Closed field should be present and the
        Due field should not be present in the detail view of a tab.
        If the tab has purchases assigned to it, then the purchases
        should be displayed in ascending order of when the purchases
        were made. The total amount of the tab should also be displayed.
        """
        tab = create_tab(
            customer=self.customer,
            closed=datetime(year=1993, month=9, day=3, hour=6, minute=10, second=32),
        )
        purchase1 = make_purchase(tab=tab, item=self.item, quantity=1, amount=6)
        purchase2 = make_purchase(tab=tab, item=self.item, quantity=2, amount=12)
        purchase3 = make_purchase(tab=tab, item=self.item, quantity=5, amount=30)
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "tabs", "id": tab.id})
        )
        self.assertContains(response, tab.opened.strftime("%Y-%m-%d %H:%M"))
        self.assertContains(response, tab.closed.strftime("%Y-%m-%d %H:%M"))
        self.assertNotContains(response, "Due")
        self.assertQuerySetEqual(tab.get_purchases(), [purchase1, purchase2, purchase3])
        self.assertContains(response, "Total: 48.00 credits")


class AllCategoriesViewTestCase(TestCase):
    def test_single_menu_category(self):
        """
        The menu categories page should display a single category if
        only one category is added.
        """
        category = models.MenuItemCategory.objects.create(name="Gin")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/categories.html")
        self.assertContains(response, "<h1>Menu</h1>")
        self.assertQuerySetEqual(response.context["categories"], [category])
        self.assertContains(response, "Gin")

    def test_multiple_menu_categories(self):
        """
        The menu categories page should display multiple categories
        sorted alphabetically.
        """
        category1 = models.MenuItemCategory.objects.create(name="Gin")
        category2 = models.MenuItemCategory.objects.create(name="Beer")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )
        self.assertQuerySetEqual(response.context["categories"], [category2, category1])

    def test_menu_category_no_inventory_categories(self):
        """
        A menu category should not show up on the inventory categories
        page.
        """
        models.MenuItemCategory.objects.create(name="Gin")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )
        self.assertNotContains(response, "Gin")
        self.assertQuerySetEqual(response.context["categories"], [])

    def test_single_inventory_category(self):
        """
        The inventory categories page should display a single category
        if only one category is added.
        """
        category = models.InventoryItemCategory.objects.create(name="Juice")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/categories.html")
        self.assertContains(response, "<h1>Inventory</h1>")
        self.assertQuerySetEqual(response.context["categories"], [category])
        self.assertContains(response, "Juice")

    def test_multiple_inventory_categories(self):
        """
        The inventory categories page should display multiple categories
        sorted alphabetically.
        """
        category1 = models.InventoryItemCategory.objects.create(name="Tequila")
        category2 = models.InventoryItemCategory.objects.create(name="Miscellaneous")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )
        self.assertQuerySetEqual(response.context["categories"], [category2, category1])

    def test_inventory_category_no_menu_categories(self):
        """
        An inventory category should not show up on the menu categories
        page.
        """
        models.InventoryItemCategory.objects.create(name="Juice")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )
        self.assertNotContains(response, "Juice")
        self.assertQuerySetEqual(response.context["categories"], [])
