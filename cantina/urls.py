from django.urls import path

from . import views

app_name = "cantina"
urlpatterns = [
    path("<str:table>/", views.view_all_instances, name="view_all"),
    path("<str:table>/add/", views.add_instance, name="add"),
    path("<str:table>/<int:id>/", views.view_instance, name="view"),
    path("purchases/<int:id>/edit/", views.edit_purchase, name="edit_purchase"),
    path("<str:table>/<int:id>/edit/", views.edit_instance, name="edit"),
    path("<str:table>/<int:id>/delete/", views.delete_instance, name="delete"),
    path("<str:table>/categories/", views.view_categories, name="view_categories"),
    path(
        "<str:table>/categories/<int:id>/",
        views.view_all_instances,
        name="view_category",
    ),
    path("<str:table>/categories/<int:id>/add/", views.add_instance, name="add_item"),
    path(
        "menu/items/<int:item>/<str:table>/add/",
        views.add_instance,
        name="menu_options",
    ),
    path("purchases/<int:id>/comp/", views.comp_purchase, name="comp_purchase"),
]
