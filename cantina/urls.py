from django.urls import path

from . import views

app_name = "cantina"
urlpatterns = [
    path("customers/", views.all_customers, name="all_customers"),
    path("customers/add/", views.add_customer, name="add_customer"),
    path("customers/<int:customer_id>/", views.customer, name="customer"),
    path(
        "customers/<int:customer_id>/edit/", views.edit_customer, name="edit_customer"
    ),
    path(
        "customers/<int:customer_id>/delete/",
        views.delete_customer,
        name="delete_customer",
    ),
    path("tabs/", views.all_tabs, name="all_tabs"),
    path("tabs/<int:tab_id>/edit", views.edit_tab, name="edit_tab"),
    path("tabs/<int:tab_id>/delete", views.delete_tab, name="delete_tab"),
    path("purchases/", views.all_purchases, name="all_purchases"),
    path("purchases/add", views.add_purchase, name="add_purchase"),
    path("purchases/<int:purchase_id>/edit", views.edit_purchase, name="edit_purchase"),
]
