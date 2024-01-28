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
        """
        If no tabs exist, an appropriate message should be displayed.
        """
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
    def test_get_request(self):
        """
        The add customer view should return a blank submission form for
        adding a customer upon receiving a GET request.
        """
        response = self.client.get(
            reverse("cantina:add", kwargs={"table": "customers"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/add_instance.html")
        self.assertContains(response, "<h1>Add Customer</h1>")
        self.assertContains(response, "Last name:")
        self.assertContains(response, "First name:")
        self.assertContains(response, "Planet:")
        self.assertContains(response, "UBA Number:")

    def test_valid_post_request(self):
        """
        The add customer view should add a customer to the database
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse("cantina:add", kwargs={"table": "customers"}),
            {
                "last_name": "Neramani",
                "first_name": "Lilandra",
                "planet": "Chandilar",
                "uba": "SHYRR8K0O1WXXP12RQHT3B6N",
            },
            follow=True,
        )
        majestrix = Customer.objects.get(last_name="Neramani")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/customers/{majestrix.id}/")
        self.assertEqual(response.templates[0].name, "cantina/customer.html")
        self.assertEqual(majestrix.last_name, "Neramani")
        self.assertEqual(majestrix.first_name, "Lilandra")
        self.assertEqual(majestrix.planet, "Chandilar")
        self.assertEqual(majestrix.uba, "SHYRR8K0O1WXXP12RQHT3B6N")

    def test_invalid_post_request(self):
        """
        The add customer view should not add a customer to the database
        if the POST request is missing required information. Required
        fields with missing values should display a message to the user
        and previously submitted information should be retained in
        the form.
        """
        response = self.client.post(
            reverse("cantina:add", kwargs={"table": "customers"}),
            {
                "last_name": "Neramani",
                "first_name": "Cal'syee",
                "planet": "",
                "uba": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, 'name="last_name" value="Neramani"')
        self.assertContains(response, 'name="first_name" value="Cal&#x27;syee"')
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(last_name="Neramani")

    def test_nonunique_customer(self):
        """
        The add customer view should not add a customer to the database
        if the customer to be added has the same name and UBA number as
        another customer in the database.
        """
        Customer.objects.create(
            last_name="Neramani",
            first_name="Cal'syee",
            planet="Aerie",
            uba="81A09JDC9KAKXGDKA5BXSAZ2",
        )
        response = self.client.post(
            reverse("cantina:add", kwargs={"table": "customers"}),
            {
                "last_name": "Neramani",
                "first_name": "Cal'syee",
                "planet": "Chandilar",
                "uba": "81A09JDC9KAKXGDKA5BXSAZ2",
            },
        )
        deathbird = Customer.objects.get(last_name="Neramani")

        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(planet="Chandilar")
        self.assertEqual(deathbird.planet, "Aerie")
        self.assertContains(
            response,
            "Customer with this Last name, First name and UBA Number already exists.",
        )


class AddMenuItemViewTestCase(TestCase):
    def setUp(self):
        self.category = MenuItemCategory.objects.create(name="Liqueur")

    def test_get_request(self):
        """
        The add menu item view should return a blank submission form
        (except for the category field) for adding a menu item upon
        receiving a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:add_item", kwargs={"table": "menu", "id": self.category.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/add_instance.html")
        self.assertContains(response, "<h1>Add Liqueur to Menu</h1>")
        self.assertContains(response, "selected>Liqueur")
        self.assertContains(response, "Name:")
        self.assertContains(response, "Price:")

    def test_valid_post_request(self):
        """
        The add menu item view should add a menu item to the database
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:add_item", kwargs={"table": "menu", "id": self.category.id}
            ),
            {"category": self.category.id, "name": "Grand Marnier", "price": 10},
            follow=True,
        )
        grand_marnier = MenuItem.objects.get(name="Grand Marnier")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/menu/{grand_marnier.id}/")
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        self.assertEqual(grand_marnier.name, "Grand Marnier")
        self.assertEqual(grand_marnier.category.name, "Liqueur")
        self.assertEqual(grand_marnier.price, 10)

    def test_invalid_post_request(self):
        """
        The add menu item view should not add a menu item to the
        database if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be retained
        in the form.
        """
        response = self.client.post(
            reverse(
                "cantina:add_item", kwargs={"table": "menu", "id": self.category.id}
            ),
            {"category": self.category.id, "name": "Grand Marnier"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.category.name}")
        self.assertContains(response, 'name="name" value="Grand Marnier"')
        with self.assertRaises(MenuItem.DoesNotExist):
            MenuItem.objects.get(name="Grand Marnier")

    def test_nonunique_menu_item(self):
        """
        The add menu item view should not add a menu item to the
        database if the menu item to be added has the same name as
        another menu item in the database.
        """
        MenuItem.objects.create(category=self.category, name="Grand Marnier", price=10)
        response = self.client.post(
            reverse(
                "cantina:add_item", kwargs={"table": "menu", "id": self.category.id}
            ),
            {"category": self.category.id, "name": "Grand Marnier", "price": 15},
        )
        grand_marnier = MenuItem.objects.get(name="Grand Marnier")

        with self.assertRaises(MenuItem.DoesNotExist):
            MenuItem.objects.get(price=15)
        self.assertEqual(grand_marnier.price, 10)
        self.assertContains(response, "Menu item with this Name already exists.")


class AddInventoryItemViewTestCase(TestCase):
    def setUp(self):
        self.category = InventoryItemCategory.objects.create(name="Cognac")

    def test_get_request(self):
        """
        The add inventory item view should return a blank submission
        form (except for the category field) for adding an inventory
        item upon receiving a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:add_item",
                kwargs={"table": "inventory", "id": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/add_instance.html")
        self.assertContains(response, "<h1>Add Cognac to Inventory</h1>")
        self.assertContains(response, "selected>Cognac")
        self.assertContains(response, "Name:")
        self.assertContains(response, "Cost:")
        self.assertContains(response, "Stock:")
        self.assertContains(response, "Reorder point:")
        self.assertContains(response, "Reorder amount:")

    def test_valid_post_request(self):
        """
        The add inventory item view should add an inventory item to the
        database according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:add_item",
                kwargs={"table": "inventory", "id": self.category.id},
            ),
            {
                "category": self.category.id,
                "name": "Asgardian Cognac",
                "cost": 70,
                "stock": 100,
                "reorder_point": 20,
                "reorder_amount": 40,
            },
            follow=True,
        )
        asgardian_cognac = InventoryItem.objects.get(name="Asgardian Cognac")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0], f"/inventory/{asgardian_cognac.id}/"
        )
        self.assertEqual(response.templates[0].name, "cantina/inventory_item.html")
        self.assertEqual(asgardian_cognac.name, "Asgardian Cognac")
        self.assertEqual(asgardian_cognac.category.name, "Cognac")
        self.assertEqual(asgardian_cognac.cost, 70)
        self.assertEqual(asgardian_cognac.stock, 100)
        self.assertEqual(asgardian_cognac.reorder_point, 20)
        self.assertEqual(asgardian_cognac.reorder_amount, 40)

    def test_invalid_post_request(self):
        """
        The add inventory item view should not add an inventory item to
        the database if the POST request is missing required
        information. Required fields with missing values should display
        a message to the user and previously submitted information
        should be retained in the form.
        """
        response = self.client.post(
            reverse(
                "cantina:add_item",
                kwargs={"table": "inventory", "id": self.category.id},
            ),
            {"category": self.category.id, "name": "Asgardian Cognac", "stock": 50},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.category.name}")
        self.assertContains(response, 'name="name" value="Asgardian Cognac"')
        self.assertContains(response, 'name="stock" value="50"')
        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(name="Asgardian Cognac")

    def test_nonunique_inventory_item(self):
        """
        The add inventory item view should not add an inventory item to
        the database if the inventory item to be added has the same
        name as another inventory item in the database.
        """
        InventoryItem.objects.create(
            category=self.category,
            name="Asgardian Cognac",
            cost=70,
            stock=100,
            reorder_point=20,
            reorder_amount=40,
        )
        response = self.client.post(
            reverse(
                "cantina:add_item",
                kwargs={"table": "inventory", "id": self.category.id},
            ),
            {
                "category": self.category.id,
                "name": "Asgardian Cognac",
                "cost": 60,
                "stock": 120,
                "reorder_point": 10,
                "reorder_amount": 30,
            },
        )
        asgardian_cognac = InventoryItem.objects.get(name="Asgardian Cognac")

        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(cost=60)
        self.assertEqual(asgardian_cognac.cost, 70)
        self.assertContains(response, "Inventory item with this Name already exists.")


class AddComponentViewTestCase(TestCase):
    def setUp(self):
        menu_category = MenuItemCategory.objects.create(name="Wine")
        inventory_category = InventoryItemCategory.objects.create(name="Wine")
        self.item = MenuItem.objects.create(
            name="Celestial Groves Chardonnay (Glass)", category=menu_category, price=6
        )
        self.ingredient = InventoryItem.objects.create(
            name="Celestial Groves Chardonnay",
            category=inventory_category,
            stock=25,
            cost=15,
            reorder_point=5,
            reorder_amount=20,
        )

    def test_get_request(self):
        """
        The add component view should return a blank submission form
        (except for the item field) for adding a component upon
        receiving a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "components"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/add_instance.html")
        self.assertContains(response, f"<h1>Add Component to {self.item.name}</h1>")
        self.assertContains(response, f"selected>{self.item.name}")
        self.assertContains(response, "Ingredient:")
        self.assertContains(response, "Amount:")

    def test_valid_post_request(self):
        """
        The add component view should add a component to the database
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "components"},
            ),
            {"item": self.item.id, "ingredient": self.ingredient.id, "amount": 5},
            follow=True,
        )
        recipe = Component.objects.get(item=self.item, ingredient=self.ingredient)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/menu/{self.item.id}/")
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        self.assertEqual(recipe.item.name, self.item.name)
        self.assertEqual(recipe.ingredient.name, self.ingredient.name)
        self.assertEqual(recipe.amount, 5)

    def test_invalid_post_request(self):
        """
        The add component view should not add a component to the
        database if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be retained
        in the form.
        """
        response = self.client.post(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "components"},
            ),
            {"item": self.item.id, "ingredient": self.ingredient.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.item.name}")
        self.assertContains(response, f"selected>{self.ingredient.name}")
        with self.assertRaises(Component.DoesNotExist):
            Component.objects.get(item=self.item, ingredient=self.ingredient)

    def test_nonunique_component(self):
        """
        The add component view should not add a component to the
        database if the component to be added has the same item and
        ingredient as another component in the database.
        """
        Component.objects.create(item=self.item, ingredient=self.ingredient, amount=5)
        response = self.client.post(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "components"},
            ),
            {"item": self.item.id, "ingredient": self.ingredient.id, "amount": 3},
        )
        recipe = Component.objects.get(item=self.item, ingredient=self.ingredient)

        with self.assertRaises(Component.DoesNotExist):
            Component.objects.get(item=self.item, ingredient=self.ingredient, amount=3)
        self.assertEqual(recipe.amount, 5)
        self.assertContains(
            response, "Component with this Item and Ingredient already exists."
        )


class AddPurchaseViewTestCase(TestCase):
    def setUp(self):
        category = MenuItemCategory.objects.create(name="Beer")
        self.item = MenuItem.objects.create(
            name="Phoenix Force IPA", category=category, price=4
        )
        self.customer = Customer.objects.create(
            last_name="Warlock",
            first_name="Adam",
            planet="Earth",
            uba="PFZK81L68I018D3591HWVNC1",
        )

    def test_get_request(self):
        """
        The add purchase view should return a blank submission form
        (except for the item field) for adding a purchase upon receiving
        a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "purchases"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/add_instance.html")
        self.assertContains(response, "<h1>Place Order</h1>")
        self.assertContains(response, f"selected>{self.item.name}")
        self.assertContains(response, f"{self.customer.name}</option>")
        self.assertContains(response, "Quantity:")

    def test_valid_post_request(self):
        """
        The add purchase view should add a purchase to the database
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "purchases"},
            ),
            {"item": self.item.id, "customer": self.customer.id, "quantity": 2},
            follow=True,
        )
        purchase = Purchase.objects.get(item=self.item)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0], f"/menu/categories/{self.item.category.id}/"
        )
        self.assertEqual(response.templates[0].name, "cantina/menu.html")
        self.assertEqual(purchase.item.name, self.item.name)
        self.assertEqual(purchase.tab.customer.name, self.customer.name)
        self.assertEqual(purchase.quantity, 2)
        self.assertEqual(purchase.amount, self.item.price * purchase.quantity)

    def test_invalid_post_request(self):
        """
        The add purchase view should not add a purchase to the
        database if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be retained
        in the form.
        """
        response = self.client.post(
            reverse(
                "cantina:menu_options",
                kwargs={"item": self.item.id, "table": "purchases"},
            ),
            {"item": self.item.id, "customer": self.customer.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.item.name}")
        self.assertContains(response, f"selected>{self.customer.name}")
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(item=self.item)


class EditCustomerViewCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            last_name="Douglas",
            first_name="Heather",
            planet="Earth",
            uba="R35BQKCL8FT389JLJ8RHADSI",
        )

    def test_customer_does_not_exist(self):
        """
        If the customer does not exist, the edit customer view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "customers", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit customer view should return a submission form with
        all of the fields filled with the customer's current values
        upon receiving a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:edit", kwargs={"table": "customers", "id": self.customer.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, f"<h1>Editing: {self.customer.name}")
        self.assertContains(
            response, f'name="last_name" value="{self.customer.last_name}"'
        )
        self.assertContains(
            response, f'name="first_name" value="{self.customer.first_name}"'
        )
        self.assertContains(response, f'name="planet" value="{self.customer.planet}"')
        self.assertContains(response, f'name="uba" value="{self.customer.uba}"')

    def test_valid_post_request(self):
        """
        The edit customer view should edit a customer's details
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:edit", kwargs={"table": "customers", "id": self.customer.id}
            ),
            {
                "last_name": "Moondragon",
                "first_name": "",
                "planet": "Earth",
                "uba": "R35BQKCL8FT389JLJ8RHADSI",
            },
            follow=True,
        )
        moondragon = Customer.objects.get(id=self.customer.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0], f"/customers/{self.customer.id}/"
        )
        self.assertEqual(response.templates[0].name, "cantina/customer.html")
        self.assertEqual(moondragon.last_name, "Moondragon")
        self.assertEqual(moondragon.first_name, "")

    def test_invalid_post_request(self):
        """
        The edit customer view should not edit a customer's information
        if the POST request is missing required information. Required
        fields with missing values should display a message to the user
        and previously submitted information should be retained in
        the form.
        """
        response = self.client.post(
            reverse(
                "cantina:edit", kwargs={"table": "customers", "id": self.customer.id}
            ),
            {
                "last_name": "Moondragon",
                "first_name": "",
                "planet": "",
                "uba": "R35BQKCL8FT389JLJ8RHADSI",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, 'name="last_name" value="Moondragon"')
        self.assertContains(response, 'name="uba" value="R35BQKCL8FT389JLJ8RHADSI"')
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(last_name="Moondragon")


class EditTabViewCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Annihilus",
            first_name="",
            planet="Arthros",
            uba="0LFCE5K0E6HWLL3DCCB8B15H",
        )
        self.tab = Tab.objects.create(customer=customer)

    def test_tab_does_not_exist(self):
        """
        If the tab does not exist, the edit tab view should return a
        404 status code.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "tabs", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit tab view should return a submission form with all of
        the fields filled with the tab's current values upon receiving
        a GET request.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "tabs", "id": self.tab.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, "<h1>Edit Tab:")
        self.assertContains(response, f"selected> {self.tab.customer.name}")
        self.assertContains(
            response, f'name="due" value="{self.tab.due.strftime("%Y-%m-%d %H:%M:%S")}"'
        )
        self.assertNotContains(response, 'name="closed" value="')

    def test_valid_post_request(self):
        """
        The edit tab view should edit a tab's details according to the
        data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "tabs", "id": self.tab.id}),
            {
                "customer": f"{self.tab.customer.id}",
                "due": f"{self.tab.due.strftime('%Y-%m-%d %H:%M:%S')}",
                "closed": "2024-01-01 18:30:15",
            },
            follow=True,
        )
        tab = Tab.objects.get(id=self.tab.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/tabs/{self.tab.id}/")
        self.assertEqual(response.templates[0].name, "cantina/tab.html")
        self.assertEqual(tab.customer.name, self.tab.customer.name)
        self.assertEqual(
            tab.due.strftime("%Y-%m-%d %H:%M:%S"),
            self.tab.due.strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            tab.closed.strftime("%Y-%m-%d %H:%M:%S"), "2024-01-01 18:30:15"
        )

    def test_invalid_post_request(self):
        """
        The edit tab view should not edit a tab's information if the
        POST request is missing required information. Required fields
        with missing values should display a message to the user and
        previously submitted information should be retained in the form.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "tabs", "id": self.tab.id}),
            {
                "customer": f"{self.tab.customer.id}",
                "due": "",
                "closed": "2024-01-01 18:30:15",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected> {self.tab.customer.name}")
        self.assertContains(response, 'name="closed" value="2024-01-01 18:30:15"')
        with self.assertRaises(Tab.DoesNotExist):
            timestamp = datetime.strptime("2024-01-01 18:30:15", "%Y-%m-%d %H:%M:%S")
            Tab.objects.get(closed=timestamp)


class EditMenuItemViewCase(TestCase):
    def setUp(self):
        category = MenuItemCategory.objects.create(name="Tequila")
        self.item = MenuItem.objects.create(
            name="Cosmic Control (Blanco)", category=category, price=8
        )

    def test_item_does_not_exist(self):
        """
        If the menu item does not exist, the edit menu item view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "menu", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit menu item view should return a submission form with
        all of the fields filled with the menu item's current values
        upon receiving a GET request.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "menu", "id": self.item.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, f"<h1>Editing: {self.item.name}")
        self.assertContains(response, f"selected>{self.item.category.name}")
        self.assertContains(response, f'name="name" value="{self.item.name}"')
        self.assertContains(response, f'name="price" value="{self.item.price}.00"')

    def test_valid_post_request(self):
        """
        The edit menu item view should edit a menu item's details
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "menu", "id": self.item.id}),
            {
                "category": f"{self.item.category.id}",
                "name": "Cosmic Control (Anejo)",
                "price": "13",
            },
            follow=True,
        )
        item = MenuItem.objects.get(id=self.item.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/menu/{self.item.id}/")
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        self.assertEqual(item.category.name, self.item.category.name)
        self.assertEqual(item.name, "Cosmic Control (Anejo)")
        self.assertEqual(item.price, 13)

    def test_invalid_post_request(self):
        """
        The edit menu item view should not edit a menu item's
        information if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be
        retained in the form.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "menu", "id": self.item.id}),
            {
                "category": f"{self.item.category.id}",
                "name": "Cosmic Control (Anejo)",
                "price": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.item.category.name}")
        self.assertContains(response, 'name="name" value="Cosmic Control (Anejo)"')
        with self.assertRaises(MenuItem.DoesNotExist):
            MenuItem.objects.get(name="Cosmic Control (Anejo)")


class EditInventoryItemViewCase(TestCase):
    def setUp(self):
        category = InventoryItemCategory.objects.create(name="Wine")
        self.item = InventoryItem.objects.create(
            name="Chitauri Orchards Champagne",
            category=category,
            stock=50,
            cost=45,
            reorder_point=10,
            reorder_amount=30,
        )

    def test_item_does_not_exist(self):
        """
        If the inventory item does not exist, the edit inventory item
        view should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "inventory", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit inventory item view should return a submission form
        with all of the fields filled with the inventory item's current
        values upon receiving a GET request.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "inventory", "id": self.item.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, f"<h1>Editing: {self.item.name}")
        self.assertContains(response, f"selected>{self.item.category.name}")
        self.assertContains(response, f'name="name" value="{self.item.name}"')
        self.assertContains(response, f'name="cost" value="{self.item.cost}.00"')
        self.assertContains(response, f'name="stock" value="{self.item.stock}.00"')
        self.assertContains(
            response, f'name="reorder_point" value="{self.item.reorder_point}"'
        )
        self.assertContains(
            response, f'name="reorder_amount" value="{self.item.reorder_amount}"'
        )

    def test_valid_post_request(self):
        """
        The edit inventory item view should edit an inventory item's
        details according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "inventory", "id": self.item.id}),
            {
                "category": f"{self.item.category.id}",
                "name": "Chitauri Orchards Champagne",
                "stock": 30,
                "cost": 50,
                "reorder_point": 15,
                "reorder_amount": 50,
            },
            follow=True,
        )
        item = InventoryItem.objects.get(id=self.item.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/inventory/{self.item.id}/")
        self.assertEqual(response.templates[0].name, "cantina/inventory_item.html")
        self.assertEqual(item.category.name, self.item.category.name)
        self.assertEqual(item.name, self.item.name)
        self.assertEqual(item.stock, 30)
        self.assertEqual(item.cost, 50)
        self.assertEqual(item.reorder_point, 15)
        self.assertEqual(item.reorder_amount, 50)

    def test_invalid_post_request(self):
        """
        The edit inventory item view should not edit an inventory item's
        information if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be
        retained in the form.
        """
        response = self.client.post(
            reverse("cantina:edit", kwargs={"table": "inventory", "id": self.item.id}),
            {
                "category": f"{self.item.category.id}",
                "name": "Chitauri Orchards Champagne",
                "stock": 30,
                "cost": "",
                "reorder_point": 15,
                "reorder_amount": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.item.category.name}")
        self.assertContains(response, f'name="name" value="{self.item.name}"')
        self.assertContains(response, 'name="stock" value="30"')
        self.assertContains(response, 'name="reorder_point" value="15"')
        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(stock=30)


class EditComponentViewCase(TestCase):
    def setUp(self):
        menu_category = MenuItemCategory.objects.create(name="Beer")
        inventory_category = InventoryItemCategory.objects.create(name="Beer")
        item = MenuItem.objects.create(
            name="Brood Brew", category=menu_category, price=4
        )
        ingredient = InventoryItem.objects.create(
            name="Brood Brew",
            category=inventory_category,
            stock=200,
            cost=1.50,
            reorder_point=40,
            reorder_amount=150,
        )
        self.recipe = Component.objects.create(
            item=item, ingredient=ingredient, amount=1
        )

    def test_component_does_not_exist(self):
        """
        If the component does not exist, the edit component view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:edit", kwargs={"table": "components", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit component view should return a submission form with
        all of the fields filled with the component's current values
        upon receiving a GET request.
        """
        response = self.client.get(
            reverse(
                "cantina:edit", kwargs={"table": "components", "id": self.recipe.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, "<h1>Edit Component:")
        self.assertContains(response, f"selected>{self.recipe.item.name}")
        self.assertContains(response, f"selected>{self.recipe.ingredient.name}")
        self.assertContains(response, f'name="amount" value="{self.recipe.amount}.00"')

    def test_valid_post_request(self):
        """
        The edit component view should edit a component's details
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse(
                "cantina:edit", kwargs={"table": "components", "id": self.recipe.id}
            ),
            {
                "item": f"{self.recipe.item.id}",
                "ingredient": f"{self.recipe.ingredient.id}",
                "amount": "2",
            },
            follow=True,
        )
        recipe = Component.objects.get(id=self.recipe.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], f"/menu/{self.recipe.item.id}/")
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        self.assertEqual(recipe.item.name, self.recipe.item.name)
        self.assertEqual(recipe.ingredient.name, self.recipe.ingredient.name)
        self.assertEqual(recipe.amount, 2)

    def test_invalid_post_request(self):
        """
        The edit component view should not edit a component's
        information if the POST request is missing required information.
        Required fields with missing values should display a message to
        the user and previously submitted information should be
        retained in the form.
        """
        brood_budget_brew = InventoryItem.objects.create(
            name="Brood Budget Brew",
            category=self.recipe.ingredient.category,
            stock=200,
            cost=0.25,
            reorder_point=50,
            reorder_amount=150,
        )
        response = self.client.post(
            reverse(
                "cantina:edit", kwargs={"table": "components", "id": self.recipe.id}
            ),
            {
                "item": f"{self.recipe.item.id}",
                "ingredient": f"{brood_budget_brew.id}",
                "amount": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.recipe.item.name}")
        self.assertContains(response, f"selected>{self.recipe.ingredient.name}")
        with self.assertRaises(Component.DoesNotExist):
            Component.objects.get(ingredient=brood_budget_brew)


class EditPurchaseViewCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Mander-Azur",
            first_name="Karnak",
            planet="Attilan",
            uba="XM85Y2UEDR5GLWWFQLK9G4A9",
        )
        tab = Tab.objects.create(customer=customer)
        category = MenuItemCategory.objects.create(name="Rum")
        item = MenuItem.objects.create(
            name="Terrigen Mists Aged Rum", category=category, price=10
        )
        self.purchase = Purchase.objects.create(
            tab=tab, item=item, quantity=1, amount=10
        )

    def test_purchase_does_not_exist(self):
        """
        If the purchase does not exist, the edit purchase view should
        return a 404 status code.
        """
        response = self.client.get(reverse("cantina:edit_purchase", kwargs={"id": 1}))

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The edit purchase view should return a submission form with all
        of the fields filled with the purchase's current values upon
        receiving a GET request.
        """
        response = self.client.get(
            reverse("cantina:edit_purchase", kwargs={"id": self.purchase.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/edit_instance.html")
        self.assertContains(response, "<h1>Edit Purchase:")
        self.assertContains(response, f"selected>{self.purchase.tab.customer.name}")
        self.assertContains(response, f"selected>{self.purchase.item.name}")
        self.assertContains(
            response, f'name="quantity" value="{self.purchase.quantity}"'
        )

    def test_valid_post_request(self):
        """
        The edit purchase view should edit a purchase's details
        according to the data submitted in a valid POST request.
        """
        response = self.client.post(
            reverse("cantina:edit_purchase", kwargs={"id": self.purchase.id}),
            {
                "customer": f"{self.purchase.tab.customer.id}",
                "item": f"{self.purchase.item.id}",
                "quantity": "2",
            },
            follow=True,
        )
        purchase = Purchase.objects.get(id=self.purchase.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0], f"/tabs/{self.purchase.tab.id}/"
        )
        self.assertEqual(response.templates[0].name, "cantina/tab.html")
        self.assertEqual(purchase.tab.id, self.purchase.tab.id)
        self.assertEqual(purchase.item.name, self.purchase.item.name)
        self.assertEqual(purchase.quantity, 2)
        self.assertEqual(purchase.amount, self.purchase.item.price * 2)

    def test_invalid_post_request(self):
        """
        The edit purchase view should not edit a purchase's information
        if the POST request is missing required information. Required
        fields with missing values should display a message to the user
        and previously submitted information should be retained in the
        form.
        """
        asteroid_m_anejo_rum = MenuItem.objects.create(
            name="Asteroid M Anejo Rum", category=self.purchase.item.category, price=15
        )
        response = self.client.post(
            reverse("cantina:edit_purchase", kwargs={"id": self.purchase.id}),
            {
                "customer": f"{self.purchase.tab.customer.id}",
                "item": f"{asteroid_m_anejo_rum.id}",
                "quantity": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f"selected>{self.purchase.tab.customer.name}")
        self.assertContains(response, f"selected>{asteroid_m_anejo_rum.name}")
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(item=asteroid_m_anejo_rum)


class DeleteCustomerViewCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            last_name="Knull",
            first_name="",
            planet="The Abyss",
            uba="",
        )

    def test_customer_does_not_exist(self):
        """
        If the customer does not exist, the delete customer view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "customers", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete customer view should delete the customer from the
        database upon receiving a GET request.
        """
        customer = Customer.objects.get(id=self.customer.id)
        self.assertEqual(customer.name, self.customer.name)

        response = self.client.get(
            reverse(
                "cantina:delete", kwargs={"table": "customers", "id": self.customer.id}
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/customers.html")
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(id=self.customer.id)


class DeleteTabViewCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Ronan",
            first_name="",
            planet="Hala",
            uba="045K9PVXZ8R6GCE58MO10G9N",
        )
        self.tab = Tab.objects.create(customer=customer)

    def test_tab_does_not_exist(self):
        """
        If the tab does not exist, the delete tab view should return a
        404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "tabs", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete tab view should delete the tab from the database
        upon receiving a GET request.
        """
        tab = Tab.objects.get(id=self.tab.id)
        self.assertEqual(tab.customer.name, self.tab.customer.name)

        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "tabs", "id": self.tab.id}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/tabs.html")
        with self.assertRaises(Tab.DoesNotExist):
            Tab.objects.get(id=self.tab.id)


class DeleteMenuItemViewCase(TestCase):
    def setUp(self):
        category = MenuItemCategory.objects.create(name="Cocktail")
        self.item = MenuItem.objects.create(
            name="The Shapeshifter", category=category, price=18
        )

    def test_item_does_not_exist(self):
        """
        If the menu item does not exist, the delete menu item view
        should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "menu", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete menu item view should delete the menu item from the
        database upon receiving a GET request.
        """
        item = MenuItem.objects.get(id=self.item.id)
        self.assertEqual(item.name, self.item.name)

        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "menu", "id": self.item.id}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/menu.html")
        with self.assertRaises(MenuItem.DoesNotExist):
            MenuItem.objects.get(id=self.item.id)


class DeleteInventoryItemViewCase(TestCase):
    def setUp(self):
        category = InventoryItemCategory.objects.create(name="Miscellaneous")
        self.item = InventoryItem.objects.create(
            name="Bloody Mary Mix",
            category=category,
            stock=80,
            cost=4,
            reorder_point=20,
            reorder_amount=60,
        )

    def test_item_does_not_exist(self):
        """
        If the inventory item does not exist, the delete inventory item
        view should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "inventory", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete inventory item view should delete the inventory item
        from the database upon receiving a GET request.
        """
        item = InventoryItem.objects.get(id=self.item.id)
        self.assertEqual(item.name, self.item.name)

        response = self.client.get(
            reverse(
                "cantina:delete", kwargs={"table": "inventory", "id": self.item.id}
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/inventory.html")
        with self.assertRaises(InventoryItem.DoesNotExist):
            InventoryItem.objects.get(id=self.item.id)


class DeleteComponentViewCase(TestCase):
    def setUp(self):
        menu_category = MenuItemCategory.objects.create(name="Liqueur")
        inventory_category = InventoryItemCategory.objects.create(name="Liqueur")
        item = MenuItem.objects.create(
            name="Baileys Irish Cream", category=menu_category, price=7
        )
        ingredient = InventoryItem.objects.create(
            name="Baileys Irish Cream",
            category=inventory_category,
            stock=120,
            cost=20,
            reorder_point=30,
            reorder_amount=80,
        )
        self.recipe = Component.objects.create(
            item=item, ingredient=ingredient, amount=1.5
        )

    def test_component_does_not_exist(self):
        """
        If the component does not exist, the delete component view
        should return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "components", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete component view should delete the component from the
        database upon receiving a GET request.
        """
        recipe = Component.objects.get(id=self.recipe.id)
        self.assertEqual(recipe.amount, self.recipe.amount)

        response = self.client.get(
            reverse(
                "cantina:delete", kwargs={"table": "components", "id": self.recipe.id}
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/menu_item.html")
        with self.assertRaises(Component.DoesNotExist):
            Component.objects.get(id=self.recipe.id)


class DeletePurchaseViewCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Rom", planet="Galador", uba="4BKV7R0CKCQLYXSKFD9I70G8"
        )
        tab = Tab.objects.create(customer=customer)
        menu_category = MenuItemCategory.objects.create(name="Cocktail")
        item = MenuItem.objects.create(
            name="Sakaar Screwdriver", category=menu_category, price=11
        )
        self.purchase = Purchase.objects.create(
            tab=tab, item=item, quantity=2, amount=22
        )

    def test_purchase_does_not_exist(self):
        """
        If the purchase does not exist, the delete purchase view should
        return a 404 status code.
        """
        response = self.client.get(
            reverse("cantina:delete", kwargs={"table": "purchases", "id": 1})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The delete purchase view should delete the purchase from the
        database upon receiving a GET request.
        """
        purchase = Purchase.objects.get(id=self.purchase.id)
        self.assertEqual(purchase.item.name, self.purchase.item.name)

        response = self.client.get(
            reverse(
                "cantina:delete", kwargs={"table": "purchases", "id": self.purchase.id}
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/tab.html")
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(id=self.purchase.id)


class CompPurchaseViewCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            last_name="Korg", planet="Ria", uba="2C505IW11KW7O99Z4IDJTT0A"
        )
        tab = Tab.objects.create(customer=customer)
        menu_category = MenuItemCategory.objects.create(name="Cocktail")
        item = MenuItem.objects.create(
            name="Dirty Badoon Martini", category=menu_category, price=14
        )
        self.purchase = Purchase.objects.create(
            tab=tab, item=item, quantity=2, amount=28
        )

    def test_purchase_does_not_exist(self):
        """
        If the purchase does not exist, the comp purchase view should
        return a 404 status code.
        """
        response = self.client.get(reverse("cantina:comp_purchase", kwargs={"id": 1}))

        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        """
        The comp purchase view should reduce the purchase amount to 0
        upon receiving a GET request.
        """
        purchase = Purchase.objects.get(id=self.purchase.id)
        self.assertEqual(purchase.amount, self.purchase.amount)

        response = self.client.get(
            reverse("cantina:comp_purchase", kwargs={"id": self.purchase.id}),
            follow=True,
        )
        purchase = Purchase.objects.get(id=self.purchase.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "cantina/tab.html")
        self.assertEqual(purchase.amount, 0)
