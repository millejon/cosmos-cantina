from django.shortcuts import get_object_or_404, render, redirect

from .models import Customer, Tab
from .data import objects


########################################################################
#                                                                      #
#                                VIEWS                                 #
#                                                                      #
########################################################################
def view_all_instances(request, table, id=None):
    if id:
        category = get_object_or_404(objects[table]["categories"], pk=id)
        instances = objects[table]["model"].objects.filter(category=category)
        context = {"instances": instances, "category": category}
    else:
        instances = objects[table]["model"].objects.all()
        context = {"instances": instances}

    return render(request, f"cantina/{table}.html", context)


def view_instance(request, table, id):
    instance = get_object_or_404(objects[table]["model"], pk=id)
    context = {"instance": instance}

    if table.endswith("s"):
        return render(request, f"cantina/{table[:-1]}.html", context)
    else:
        return render(request, f"cantina/{table}_item.html", context)


def view_categories(request, table):
    categories = objects[table]["categories"].objects.all()
    context = {"categories": categories, "table": table}
    return render(request, "cantina/categories.html", context)


def add_instance(request, table, id=None, item=None):
    category = get_object_or_404(objects[table]["categories"], pk=id) if id else None
    item = get_object_or_404(objects["menu"]["model"], pk=item) if item else None

    if request.method == "POST":
        form = objects[table]["form"](data=request.POST)

        if form.is_valid():
            if table == "purchases":
                purchase = form.save(commit=False)
                purchase.tab = get_tab(request.POST["customer"])
                purchase.update_amount()
                purchase.save()
                return redirect(
                    "cantina:view_category", table="menu", id=item.category.id
                )
            elif table == "components":
                form.save()
                return redirect("cantina:view", table="menu", id=item.id)
            else:
                instance = form.save()
                return redirect("cantina:view", table=table, id=instance.id)
    else:
        form = objects[table]["form"](initial={"category": category, "item": item})

    context = {"form": form, "table": table, "category": category, "item": item}
    return render(request, "cantina/add_instance.html", context)


def edit_instance(request, table, id):
    instance = get_object_or_404(objects[table]["model"], pk=id)

    if request.method == "POST":
        form = objects[table]["form"](instance=instance, data=request.POST)

        if form.is_valid():
            form.save()
            if table == "components":
                return redirect("cantina:view", table="menu", id=instance.item.id)
            else:
                return redirect("cantina:view", table=table, id=id)
    else:
        form = objects[table]["form"](instance=instance)

    context = {"instance": instance, "form": form, "table": table}
    return render(request, "cantina/edit_instance.html", context)


def edit_purchase(request, id):
    purchase = get_object_or_404(objects["purchases"]["model"], pk=id)

    if request.method == "POST":
        form = objects["purchases"]["form"](instance=purchase, data=request.POST)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.tab = get_tab(request.POST["customer"])
            purchase.update_amount()
            purchase.save()
            return redirect("cantina:view", table="tabs", id=purchase.tab.id)
    else:
        form = objects["purchases"]["form"](
            initial={"customer": purchase.tab.customer}, instance=purchase
        )

    context = {"instance": purchase, "form": form, "table": "purchases"}
    return render(request, "cantina/edit_instance.html", context)


def delete_instance(request, table, id):
    instance = get_object_or_404(objects[table]["model"], pk=id)
    instance.delete()

    if table == "purchases":
        return redirect("cantina:view", table="tabs", id=instance.tab.id)
    elif table == "components":
        return redirect("cantina:view", table="menu", id=instance.item.id)
    elif not table.endswith("s"):
        return redirect("cantina:view_category", table=table, id=instance.category.id)
    else:
        return redirect("cantina:view_all", table=table)


def comp_purchase(request, id):
    purchase = get_object_or_404(objects["purchases"]["model"], pk=id)
    purchase.comp()
    purchase.save()

    return redirect("cantina:view", table="tabs", id=purchase.tab.id)


########################################################################
#                                                                      #
#                           HELPER FUNCTIONS                           #
#                                                                      #
########################################################################
def get_tab(customer: int) -> Tab:
    """
    Return customer's open tab or, if the customer does not currently
    have an open tab, create one and return.
    """
    customer = Customer.objects.get(pk=customer)
    try:
        tab = customer.tab_set.get(closed__isnull=True)
    except Tab.DoesNotExist:
        tab = Tab.objects.create(customer=customer)
        tab.save()

    return tab
