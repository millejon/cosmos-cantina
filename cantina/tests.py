from django.test import TestCase
from django.urls import reverse
from datetime import datetime

from .models import (
    Customer,
    Tab,
    Purchase,
    MenuItemCategory,
    MenuItem,
    InventoryItemCategory,
    InventoryItem,
    Component,
)


class CustomerTestCase(TestCase):
    def test_customer_names(self):
        """
        The name attribute of the Customer model should return the
        customer's full name, whether the customer has a first name or
        not.
        """
        silver_surfer = Customer.objects.create(
            last_name="Radd",
            first_name="Norrin",
            planet="Zenn-La",
            uba="OHCMSZ9QF928JZNS4H20IKXP",
        )
        galactus = Customer.objects.create(
            last_name="Galactus", first_name="", planet="Galan", uba=""
        )

        self.assertEqual(silver_surfer.name, "Norrin Radd")
        self.assertEqual(galactus.name, "Galactus")


class TabTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Thanos", first_name="", planet="Titan", uba=""
        )
        self.tab = Tab.objects.create(customer=customer)
        category = MenuItemCategory.objects.create(name="Beer")
        self.item = MenuItem.objects.create(
            name="Duff Beer", category=category, price=5
        )

    def test_tab_get_purchases_with_single_purchase(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with a single
        purchase should return 1.
        """
        Purchase.objects.create(tab=self.tab, item=self.item, quantity=2, amount=10)

        self.assertEqual(len(self.tab.get_purchases()), 1)

    def test_tab_get_purchases_with_multiple_purchases(self):
        """
        The get_purchases method of the Tab model should return the
        number of purchases assigned to the tab. A tab with five
        purchases should return 5.
        """
        for _ in range(5):
            Purchase.objects.create(tab=self.tab, item=self.item, quantity=2, amount=10)

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
        Purchase.objects.create(tab=self.tab, item=self.item, quantity=3, amount=15)

        self.assertEqual(self.tab.get_amount(), 15)

    def test_tab_get_amount_with_multiple_purchase(self):
        """
        The get_amount method of the Tab model should return the total
        price of all purchases assigned to the tab.
        """
        for _ in range(5):
            Purchase.objects.create(tab=self.tab, item=self.item, quantity=4, amount=20)

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
            Purchase.objects.create(tab=self.tab, item=self.item, quantity=2, amount=10)

        self.assertEqual(self.tab.get_amount(), 50)

        purchase = self.tab.purchase_set.all()[0]
        purchase.comp()
        purchase.save()

        self.assertEqual(self.tab.get_amount(), 40)


class PurchaseTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Quill", first_name="Peter", planet="Earth", uba=""
        )
        tab = Tab.objects.create(customer=customer)
        category = MenuItemCategory.objects.create(name="Wine")
        item = MenuItem.objects.create(name="Shi'ar Sake", category=category, price=7)
        self.purchase = Purchase.objects.create(
            tab=tab, item=item, quantity=2, amount=14
        )

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
        captain_marvel = Customer.objects.create(
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
        gladiator = Customer.objects.create(
            last_name="Kallark",
            first_name="",
            planet="Strontia",
            uba="Y551W20W1AEMKJYRUP53THER",
        )
        beta_ray_bill = Customer.objects.create(
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
        Customer.objects.create(
            last_name="Raccoon", first_name="Rocket", planet="Halfworld", uba=""
        )
        Customer.objects.create(
            last_name="Groot", first_name="", planet="Planet X", uba=""
        )

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
        rocket_racoon = Customer.objects.get(last_name="Raccoon")
        tab = Tab.objects.create(customer=rocket_racoon)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "tabs"})
        )

        self.assertQuerySetEqual(response.context["instances"], [tab])

    def test_multiple_tabs(self):
        """
        The tabs page should display multiple tabs sorted by the time
        they were opened in descending order.
        """
        rocket_racoon = Customer.objects.get(last_name="Raccoon")
        groot = Customer.objects.get(last_name="Groot")
        tab1 = Tab.objects.create(customer=rocket_racoon)
        tab2 = Tab.objects.create(customer=groot)
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "tabs"})
        )

        self.assertQuerySetEqual(response.context["instances"], [tab2, tab1])


class AllPurchasesViewTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Titan", first_name="Gamora", planet="Zen-Whoberi", uba=""
        )
        self.tab = Tab.objects.create(customer=customer)
        cocktail = MenuItemCategory.objects.create(name="Cocktail")
        self.item = MenuItem.objects.create(
            name="Infinity Watch", category=cocktail, price=12
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
        purchase = Purchase.objects.create(
            tab=self.tab, item=self.item, quantity=1, amount=12
        )
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "purchases"})
        )

        self.assertQuerySetEqual(response.context["instances"], [purchase])

    def test_multiple_purchases(self):
        """
        The purchases page should display multiple purchases sorted by
        the time they were made in descending order.
        """
        purchase1 = Purchase.objects.create(
            tab=self.tab, item=self.item, quantity=3, amount=36
        )
        purchase2 = Purchase.objects.create(
            tab=self.tab, item=self.item, quantity=2, amount=24
        )
        response = self.client.get(
            reverse("cantina:view_all", kwargs={"table": "purchases"})
        )

        self.assertQuerySetEqual(response.context["instances"], [purchase2, purchase1])


class CustomerDetailsViewTestCase(TestCase):
    def test_customer_does_not_exist(self):
        """
        If the customer does not exist, the customer detail view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "customers", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_customer_with_no_uba(self):
        """
        The detail view of a customer should display information about
        the customer. If a customer does not have a UBA number, the
        field should not be present.
        """
        drax = Customer.objects.create(
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
        should display it along with the rest of the customer
        information. If the customer has not opened any tabs, there
        should be no 'Account History' section.
        """
        black_bolt = Customer.objects.create(
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
        If the customer has open tabs, the detail view for the
        customer should list the open tab, followed by the closed tabs
        in descending order of when they were closed.
        """
        medusa = Customer.objects.create(
            last_name="Amaquelin",
            first_name="Medusalith",
            planet="Attilan",
            uba="KLVREX6N766S014EN01CELID",
        )
        tab1 = Tab.objects.create(
            customer=medusa,
            closed=datetime(year=2023, month=12, day=26, hour=19, minute=20, second=14),
        )
        tab2 = Tab.objects.create(customer=medusa)
        tab3 = Tab.objects.create(
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
        self.customer = Customer.objects.create(
            last_name="Summers",
            first_name="Gabriel",
            planet="Chandilar",
            uba="P86KIIMSJRG5AMPEPZ16A1ZO",
        )
        wine = MenuItemCategory.objects.create(name="Wine")
        self.item = MenuItem.objects.create(
            name="Skrull Vineyards Pinot Noir", category=wine, price=6
        )

    def test_no_tabs(self):
        """
        If the tab does not exist, the tab detail view should return a
        404 status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "tabs", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_open_tab_with_no_purchases(self):
        """
        The detail view of a tab should display information about the
        tab. If a tab is still open, the Due field should be present
        and the Closed field should not be present. If the tab has no
        purchases assigned to it, then an appropriate message should be
        displayed.
        """
        tab = Tab.objects.create(customer=self.customer)
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
        Due field should not be present. If the tab has purchases
        assigned to it, then the purchases should be displayed in
        ascending order of when the purchases were made. The total
        amount of the tab should also be displayed.
        """
        tab = Tab.objects.create(
            customer=self.customer,
            closed=datetime(year=1993, month=9, day=3, hour=6, minute=10, second=32),
        )
        purchase1 = Purchase.objects.create(
            tab=tab, item=self.item, quantity=1, amount=6
        )
        purchase2 = Purchase.objects.create(
            tab=tab, item=self.item, quantity=2, amount=12
        )
        purchase3 = Purchase.objects.create(
            tab=tab, item=self.item, quantity=5, amount=30
        )
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "tabs", "id": tab.id})
        )

        self.assertContains(response, tab.opened.strftime("%Y-%m-%d %H:%M"))
        self.assertContains(response, tab.closed.strftime("%Y-%m-%d %H:%M"))
        self.assertNotContains(response, "Due")
        self.assertQuerySetEqual(tab.get_purchases(), [purchase1, purchase2, purchase3])
        self.assertContains(response, "Total: 48.00 credits")


class AllMenuCategoriesViewTestCase(TestCase):
    def test_single_menu_category(self):
        """
        The menu categories page should display a single category if
        only one category is added.
        """
        gin = MenuItemCategory.objects.create(name="Gin")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/categories.html")
        self.assertContains(response, "<h1>Menu</h1>")
        self.assertQuerySetEqual(response.context["categories"], [gin])
        self.assertContains(response, "Gin")

    def test_multiple_menu_categories(self):
        """
        The menu categories page should display multiple categories
        sorted alphabetically.
        """
        gin = MenuItemCategory.objects.create(name="Gin")
        beer = MenuItemCategory.objects.create(name="Beer")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )

        self.assertQuerySetEqual(response.context["categories"], [beer, gin])

    def test_menu_category_no_inventory_categories(self):
        """
        A menu category should not show up on the inventory categories
        page.
        """
        MenuItemCategory.objects.create(name="Gin")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )

        self.assertNotContains(response, "Gin")
        self.assertQuerySetEqual(response.context["categories"], [])


class AllInventoryCategoriesViewTestCase(TestCase):
    def test_single_inventory_category(self):
        """
        The inventory categories page should display a single category
        if only one category is added.
        """
        vodka = InventoryItemCategory.objects.create(name="Vodka")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/categories.html")
        self.assertContains(response, "<h1>Inventory</h1>")
        self.assertQuerySetEqual(response.context["categories"], [vodka])
        self.assertContains(response, "Vodka")

    def test_multiple_inventory_categories(self):
        """
        The inventory categories page should display multiple categories
        sorted alphabetically.
        """
        tequila = InventoryItemCategory.objects.create(name="Tequila")
        miscellaneous = InventoryItemCategory.objects.create(name="Miscellaneous")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "inventory"})
        )

        self.assertQuerySetEqual(
            response.context["categories"], [miscellaneous, tequila]
        )

    def test_inventory_category_no_menu_categories(self):
        """
        An inventory category should not show up on the menu categories
        page.
        """
        InventoryItemCategory.objects.create(name="Juice")
        response = self.client.get(
            reverse("cantina:view_categories", kwargs={"table": "menu"})
        )

        self.assertNotContains(response, "Juice")
        self.assertQuerySetEqual(response.context["categories"], [])


class MenuCategoryViewTestCase(TestCase):
    def setUp(self):
        self.category = MenuItemCategory.objects.create(name="Cocktail")

    def test_no_menu_items(self):
        """
        If no menu items exist in a category, an appropriate message
        should be displayed.
        """
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "menu", "id": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/menu.html")
        self.assertContains(response, "No cocktail is available.")
        self.assertQuerySetEqual(response.context["instances"], [])

    def test_single_menu_item(self):
        """
        The menu category should display a single item if only one item
        is added.
        """
        marvelous_manhattan = MenuItem.objects.create(
            name="Marvelous Manhattan", category=self.category, price=11
        )
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "menu", "id": self.category.id},
            )
        )

        self.assertQuerySetEqual(response.context["instances"], [marvelous_manhattan])

    def test_multiple_menu_items(self):
        """
        The menu category should display multiple items sorted
        alphabetically.
        """
        saber_fury = MenuItem.objects.create(
            name="S.A.B.E.R. Fury", category=self.category, price=13
        )
        kings_whisper = MenuItem.objects.create(
            name="King's Whisper", category=self.category, price=12
        )
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "menu", "id": self.category.id},
            )
        )

        self.assertQuerySetEqual(
            response.context["instances"], [kings_whisper, saber_fury]
        )


class InventoryCategoryViewTestCase(TestCase):
    def setUp(self):
        self.category = InventoryItemCategory.objects.create(name="Juice")

    def test_no_inventory_items(self):
        """
        If no inventory items exist in a category, an appropriate
        message should be displayed.
        """
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "inventory", "id": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/inventory.html")
        self.assertContains(response, "No juice is available.")
        self.assertQuerySetEqual(response.context["instances"], [])

    def test_single_inventory_item(self):
        """
        The inventory category should display a single item if only one
        item is added.
        """
        lime_juice = InventoryItem.objects.create(
            name="Lime Juice",
            category=self.category,
            stock=10,
            cost=4,
            reorder_point=20,
            reorder_amount=60,
        )
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "inventory", "id": self.category.id},
            )
        )

        self.assertQuerySetEqual(response.context["instances"], [lime_juice])

    def test_multiple_inventory_items(self):
        """
        The inventory category should display multiple items sorted
        alphabetically.
        """
        lemon_juice = InventoryItem.objects.create(
            name="Lemon Juice",
            category=self.category,
            stock=6,
            cost=3,
            reorder_point=2,
            reorder_amount=10,
        )
        orange_juice = InventoryItem.objects.create(
            name="Orange Juice",
            category=self.category,
            stock=15,
            cost=6,
            reorder_point=10,
            reorder_amount=50,
        )
        response = self.client.get(
            reverse(
                "cantina:view_category",
                kwargs={"table": "inventory", "id": self.category.id},
            )
        )

        self.assertQuerySetEqual(
            response.context["instances"], [lemon_juice, orange_juice]
        )


class MenuItemDetailsViewTestCase(TestCase):
    def setUp(self):
        self.category = MenuItemCategory.objects.create(name="Cocktail")

    def test_no_menu_item(self):
        """
        If the menu item does not exist, the menu item detail view
        should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "menu", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_menu_item_with_no_components(self):
        """
        The detail view of a menu item should display information about
        the menu item. If no components have been added, an appropriate
        message should be displayed.
        """
        multiversal_madness = MenuItem.objects.create(
            name="Multiversal Madness", category=self.category, price=16
        )
        response = self.client.get(
            reverse(
                "cantina:view", kwargs={"table": "menu", "id": multiversal_madness.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        self.assertContains(response, f"{multiversal_madness.name} [Cocktail]")
        self.assertContains(response, f"Price: {multiversal_madness.price}")
        self.assertContains(response, "No components have been added.")

    def test_menu_item_with_components(self):
        """
        If the menu item has components, the detail view of the item
        should list the components alphabetically and the amount
        required of each component.
        """
        multiversal_madness = MenuItem.objects.create(
            name="Multiversal Madness", category=self.category, price=16
        )
        tequila = InventoryItemCategory.objects.create(name="Tequila")
        kirby = InventoryItem.objects.create(
            name="Kirby Tequila",
            category=tequila,
            stock=100,
            cost=80,
            reorder_point=10,
            reorder_amount=60,
        )
        juice = InventoryItemCategory.objects.create(name="Juice")
        lime_juice = InventoryItem.objects.create(
            name="Lime Juice",
            category=juice,
            stock=200,
            cost=5,
            reorder_point=50,
            reorder_amount=150,
        )
        component1 = Component.objects.create(
            item=multiversal_madness, ingredient=kirby, amount=2
        )
        component2 = Component.objects.create(
            item=multiversal_madness, ingredient=lime_juice, amount=1
        )
        response = self.client.get(
            reverse(
                "cantina:view", kwargs={"table": "menu", "id": multiversal_madness.id}
            )
        )

        self.assertContains(response, "oz.")
        self.assertQuerySetEqual(
            multiversal_madness.component_set.all(), [component1, component2]
        )


class InventoryItemDetailsViewTestCase(TestCase):
    def setUp(self):
        self.category = InventoryItemCategory.objects.create(name="Miscellaneous")

    def test_no_inventory_item(self):
        """
        If the inventory item does not exist, the inventory item detail
        view should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:view", kwargs={"table": "inventory", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_inventory_item(self):
        """
        The detail view of an inventory item should display information
        about the inventory item.
        """
        agave_nectar = InventoryItem.objects.create(
            name="Agave Nectar",
            category=self.category,
            stock=100,
            cost=8,
            reorder_point=10,
            reorder_amount=60,
        )
        response = self.client.get(
            reverse(
                "cantina:view", kwargs={"table": "inventory", "id": agave_nectar.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/inventory_item.html")
        self.assertContains(response, f"{agave_nectar.name} [Miscellaneous]")
        self.assertContains(response, f"Stock: {agave_nectar.stock}")
        self.assertContains(response, f"Cost: {agave_nectar.cost}")
        self.assertContains(response, f"Reorder Point: {agave_nectar.reorder_point}")
        self.assertContains(response, f"Reorder Amount: {agave_nectar.reorder_amount}")


class AddCustomerViewTestCase(TestCase):
    pass
