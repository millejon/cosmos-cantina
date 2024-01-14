from django.shortcuts import render

from . import models


def view_all_customers(request):
    customers = models.Customer.objects.all()
    context = {"customers": customers}
    return render(request, "cantina/all_customers.html", context)
