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
]
