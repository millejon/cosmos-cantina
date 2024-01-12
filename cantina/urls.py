from django.urls import path

from . import views

app_name = "cantina"
urlpatterns = [
    path("customers/", views.view_all_customers, name="view_all_customers"),
]
