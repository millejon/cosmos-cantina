from django.shortcuts import get_object_or_404, render, redirect

from . import forms, models


def all_customers(request):
    customers = models.Customer.objects.all()
    context = {"customers": customers}
    return render(request, "cantina/all_customers.html", context)


def customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    tabs = customer.tab_set.all()
    context = {"customer": customer, "tabs": tabs}
    return render(request, "cantina/customer.html", context)


def add_customer(request):
    if request.method == "POST":
        form = forms.CustomerForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("cantina:all_customers")
    else:
        form = forms.CustomerForm()

    context = {"form": form}
    return render(request, "cantina/add_customer.html", context)


def edit_customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)

    if request.method == "POST":
        form = forms.CustomerForm(instance=customer, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("cantina:customer", customer_id=customer.id)
    else:
        form = forms.CustomerForm(instance=customer)

    context = {"customer": customer, "form": form}
    return render(request, "cantina/edit_customer.html", context)


def delete_customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    customer.delete()
    return redirect("cantina:all_customers")


def all_tabs(request):
    tabs = models.Tab.objects.all()
    context = {"tabs": tabs}
    return render(request, "cantina/all_tabs.html", context)
