# Generated by Django 5.0 on 2024-01-22 01:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cantina", "0003_rename_ingredientcategory_inventoryitemcategory_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="inventoryitemcategory",
            options={
                "ordering": ["name"],
                "verbose_name_plural": "Inventory categories",
            },
        ),
        migrations.AlterModelOptions(
            name="tab",
            options={"ordering": ["-closed", "customer__last_name"]},
        ),
        migrations.AddField(
            model_name="purchase",
            name="amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=40),
        ),
    ]
