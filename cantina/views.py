from django.shortcuts import get_object_or_404, render

from . import models


def all_customers(request):
    customers = models.Customer.objects.all()
    context = {"customers": customers}
    return render(request, "cantina/all_customers.html", context)


def customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    tabs = customer.tab_set.all()
    context = {"customer": customer, "tabs": tabs}
    return render(request, "cantina/customer.html", context)
