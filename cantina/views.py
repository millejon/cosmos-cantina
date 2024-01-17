from django.shortcuts import get_object_or_404, render, redirect

from . import forms, models


########################################################################
#                                                                      #
#                                VIEWS                                 #
#                                                                      #
########################################################################
def all_customers(request):
    customers = models.Customer.objects.all()
    context = {"customers": customers}
    return render(request, "cantina/all_customers.html", context)


def customer_detail(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    context = {"customer": customer}
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
            return redirect("cantina:customer_detail", customer_id=customer.id)
    else:
        form = forms.CustomerForm(instance=customer)

    context = {"customer": customer, "form": form}
    return render(request, "cantina/edit_customer.html", context)


def delete_customer(request, customer_id):
    customer = get_object_or_404(models.Customer, pk=customer_id)
    customer.delete()
    return redirect("cantina:all_customers")


def menu(request):
    categories = models.DrinkCategory.objects.all()
    context = {"categories": categories}
    return render(request, "cantina/menu.html", context)


def menu_category(request, category_id):
    category = get_object_or_404(models.DrinkCategory, pk=category_id)
    items = models.Drink.objects.filter(category=category)
    context = {"category": category, "items": items}
    return render(request, "cantina/menu_category.html", context)


def menu_detail(request, drink_id):
    drink = get_object_or_404(models.Drink, pk=drink_id)
    recipe = models.Recipe.objects.filter(drink=drink)
    context = {"drink": drink, "recipe": recipe}
    return render(request, "cantina/drink.html", context)


def add_purchase(request, drink_id):
    drink = get_object_or_404(models.Drink, pk=drink_id)

    if request.method == "POST":
        form = forms.PurchaseForm(data=request.POST)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.tab = get_tab(request.POST["customer"])
            purchase.save()
            return redirect("cantina:menu_category", category_id=drink.category.id)
    else:
        form = forms.PurchaseForm(initial={"drink": drink})

    context = {"drink": drink, "form": form}
    return render(request, "cantina/add_purchase.html", context)


def edit_menu(request, drink_id):
    drink = get_object_or_404(models.Drink, pk=drink_id)
    recipe = models.Recipe.objects.filter(drink=drink)

    if request.method == "POST":
        form = forms.DrinkForm(instance=drink, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("cantina:menu_category", category_id=drink.category.id)
    else:
        form = forms.DrinkForm(instance=drink)

    context = {"drink": drink, "recipe": recipe, "form": form}
    return render(request, "cantina/edit_menu.html", context)


def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(models.Recipe, pk=recipe_id)

    if request.method == "POST":
        form = forms.RecipeForm(instance=recipe, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("cantina:menu_detail", drink_id=recipe.drink.id)
    else:
        form = forms.RecipeForm(instance=recipe)

    context = {"recipe": recipe, "form": form}
    return render(request, "cantina/edit_recipe.html", context)


def all_tabs(request):
    tabs = models.Tab.objects.all()
    context = {"tabs": tabs}
    return render(request, "cantina/all_tabs.html", context)


def tab(request, tab_id):
    tab = get_object_or_404(models.Tab, pk=tab_id)
    purchases = tab.purchase_set.all()
    context = {"tab": tab, "purchases": purchases}
    return render(request, "cantina/tab.html", context)


def edit_tab(request, tab_id):
    tab = get_object_or_404(models.Tab, pk=tab_id)

    if request.method == "POST":
        form = forms.TabForm(instance=tab, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("cantina:all_tabs")  # Change this back to tab detail view
    else:
        form = forms.TabForm(instance=tab)

    context = {"tab": tab, "form": form}
    return render(request, "cantina/edit_tab.html", context)


def delete_tab(request, tab_id):
    tab = get_object_or_404(models.Tab, pk=tab_id)
    tab.delete()
    return redirect("cantina:all_tabs")


def all_purchases(request):
    purchases = models.Purchase.objects.all()
    context = {"purchases": purchases}
    return render(request, "cantina/all_purchases.html", context)


def edit_purchase(request, purchase_id):
    purchase = get_object_or_404(models.Purchase, pk=purchase_id)

    if request.method == "POST":
        form = forms.PurchaseForm(instance=purchase, data=request.POST)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.tab = get_tab(request.POST["customer"])
            purchase.save()
            return redirect(
                "cantina:all_purchases"
            )  # Change this back to purchase detail view
    else:
        customer = (
            purchase.tab.customer.id,
            f"{purchase.tab.customer.first_name} {purchase.tab.customer.last_name}",
        )
        form = forms.PurchaseForm(initial={"customer": customer}, instance=purchase)

    context = {"purchase": purchase, "form": form}
    return render(request, "cantina/edit_purchase.html", context)


def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(models.Purchase, pk=purchase_id)
    purchase.delete()
    return redirect("cantina:all_purchases")


def inventory(request):
    inventory = models.Ingredient.objects.all()
    context = {"inventory": inventory}
    return render(request, "cantina/inventory.html", context)


########################################################################
#                                                                      #
#                           HELPER FUNCTIONS                           #
#                                                                      #
########################################################################
def get_tab(customer: str) -> models.Tab:
    """
    Return customer's open tab or, if the customer does not currently
    have an open tab, create one and return.
    """
    customer = models.Customer.objects.get(pk=customer)
    try:
        tab = customer.tab_set.get(closed__isnull=True)
    except models.Tab.DoesNotExist:
        tab = models.Tab(customer=customer)
        tab.save()

    return tab
