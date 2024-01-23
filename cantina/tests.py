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

    def test_customer_name(self):
        silver_surfer = models.Customer.objects.get(last_name="Radd")
        galactus = models.Customer.objects.get(last_name="Galactus")
        self.assertEqual(silver_surfer.name, "Norrin Radd")
        self.assertEqual(galactus.name, "Galactus")
