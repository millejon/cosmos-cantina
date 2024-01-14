from django.urls import path

from . import views

app_name = "cantina"
urlpatterns = [
    path("customers/", views.all_customers, name="all_customers"),
    path("customers/<int:customer_id>/", views.customer, name="customer"),
]
