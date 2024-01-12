from django.shortcuts import render

from . import models


def view_all_customers(request):
    customers = models.Customer.objects.order_by("last_name")
    context = {"customers": customers}
    return render(request, "cantina/all_customers.html", context)
