from django import views
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import Sum, Avg, Count, Q, OuterRef, Subquery
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import render_to_string
import time

from .models import *
from .context_processors import cart as user_cart

# Create your views here.
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "shoppingwonder/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "shoppingwonder/login.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request,
                "shoppingwonder/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "shoppingwonder/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "shoppingwonder/register.html")


def index(request):
    # Get all active products
    products = Product.objects.filter(active=True, parent=None).order_by("title")
    category_name = "All"

    # Get the GET parameter "c" for category
    try:
        category_id = int(request.GET.get("c"))

        # Get that category (if it does not exist, it will throw an exception "DoesNotExist error")
        category = Category.objects.get(pk=category_id)

        # filter products under that category
        products = products.filter(category=category)
        category_name = category.name

    except Exception:
        pass

    # Get the GET parameter "v" for view
    try:
        view = request.GET.get("v")

        # Get last 3 of products created
        if view == "new":
            products = products.order_by("-created")[:3]
            category_name = "New"

        # Get top 3 sold products
        if view == "best":
            products = products.filter(sold__gt=0).order_by("-sold")[:3]
            category_name = "Best Sellers"

    except Exception:
        pass

    # Get the GET parameter "q"
    try:
        search = request.GET.get("q")

        # Search product with title containing the search value
        products = products.filter(title__icontains=search)
        category_name = "Search results for: "+search

    except Exception:
        pass

    # Pagination 9 posts/page
    p = Paginator(products, 9)

    # Display the first page
    page = p.page(1)

    # Get the GET parameter "p"
    try:
        page_num = int(request.GET.get("p"))

        # If there's get parameter and in the page range, display the requested page
        page = p.page(page_num)

    except:
        pass

    return render(
        request,
        "shoppingwonder/index.html",
        {"products": page.object_list, "category_name": category_name, "page": page},
    )


def contact(request):
    return render(request, "shoppingwonder/contact.html")


def profile(request):
    return render(request, "shoppingwonder/profile.html")


def product(request, parent_id):
    # Get the product
    try:
        parent = Product.objects.get(pk=parent_id, parent=None)
        fav_toggle = False

        # Add view count by 1 to the parent product
        parent.views +=1
        parent.save()

        if request.user.is_authenticated:
            # If the item is already on the user's favorites, toggle_fav is true
            if parent.watchers.filter(pk=request.user.pk):
                fav_toggle = True

        return render(
            request,
            "shoppingwonder/product.html",
            {
                "parent": parent,
                "fav_toggle": fav_toggle,
            },
        )

    except ObjectDoesNotExist :
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url="login")
def toggle_fav(request, parent_id):
    try:
        # Get the login user
        login_user = User.objects.get(pk=request.user.id)

        # Remove parent product from favorites if the product is currently in the user's favorites
        if login_user.favorites.filter(pk=parent_id).exists():
            login_user.favorites.remove(parent_id)
            fav_toggle = False

        # Add parent product to favorites if not yet in the user's favorites
        else:
            login_user.favorites.add(parent_id)
            fav_toggle = True
        return JsonResponse({"fav_toggle": fav_toggle})

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("product", parent_id=parent_id))


@login_required(login_url="login")
def favorites(request):
    # Get all products that user is the watcher
    products = request.user.favorites.all()
    return render(request, "shoppingwonder/favorites.html", {"products": products})


@csrf_exempt
@login_required(login_url="login")
def cart(request, product_id, action):
    if request.method == "PUT":
        if action not in ["add", "remove"]:
            return JsonResponse({}, status=400)

        try:
            # Get the product with its remaining quantity > 0
            product = Product.objects.get(pk=product_id, remaining_qty__gt=0)

            # If product record exists in user's cart, add product quantity by 1
            try:
                cart = CartItem.objects.get(shopper=request.user, product=product_id)
                if action == "add" and product.remaining_qty > cart.quantity:
                    cart.quantity = cart.quantity + 1
                    cart.save()
                if action == "remove":
                    cart.quantity = cart.quantity - 1
                    cart.save()
                    if cart.quantity == 0:
                        cart.delete()
                return get_cart_response(request)

            # Otherwise, create a new product record with quantity of 1
            except ObjectDoesNotExist:
                if action == "add":
                    create_product = CartItem(shopper=request.user, product=product, quantity=1)
                    create_product.save()
                    return get_cart_response(request)

                return JsonResponse({}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({}, status=400)

    else:
        return render(request, "shoppingwonder/index.html")


def get_cart_response(request):
    cart_context = user_cart(request)
    cart_page = render_to_string("shoppingwonder/cart.html", cart_context)
    cart_count = cart_context["cart_count"]
    return JsonResponse({"cartPage": cart_page, "cartCount": cart_count})


@csrf_exempt
@login_required(login_url="login")
def order(request):
    if request.method == "POST":
        # Get cart amount from context
        cart_context = user_cart(request)
        cart_amount = cart_context["cart_amount"]

        # Create SO
        if cart_amount > 0:
            SO = SalesOrder(customer=request.user, amount=cart_amount)
            SO.save()

            # Get product and quantity from cart
            cart_items = CartItem.objects.filter(shopper=request.user)

            for cart_item in cart_items:
                if cart_item.product.is_sellable():
                    # Add to Sales Order line items
                    SO_line = SalesOrderLineItem(sales_order=SO, product=cart_item.product, quantity=cart_item.quantity,
                        unit_price=cart_item.product.RSP)
                    SO_line.save()

                    # Reduce product remaining qty and increase sold qty for product and parent (if any)
                    cart_item.product.adjust_qty(-cart_item.quantity)
                    cart_item.product.adjust_sold(cart_item.quantity)

                    # To keep track of stock update
                    quantity = cart_item.quantity
                    while quantity > 0:
                        # Get the stock with remaining qty and link to the SO line
                        stock = Stock.objects.filter(product=cart_item.product, available_for_sales__gt=0).order_by("created").first()
                        SO_line.stocks.add(stock)

                        # Reduce the stock available and cart qty for sale with the minimum qty between cart qty and stock qty
                        min_qty = min(quantity, stock.available_for_sales)
                        quantity -= min_qty
                        stock.available_for_sales -= min_qty
                        stock.save()

            # Update SO status to "ordered"
            SO_status = SalesOrderStatus(sales_order=SO, status="1")
            SO_status.save()

            # Delete the cart items
            cart_items.delete()
            return HttpResponseRedirect(reverse("purchases"))

    return HttpResponseRedirect(reverse("index"))


@staff_member_required
def stocks(request):
    # Get the GET parameter
    view = request.GET.get("v")

    # Get parent products
    products = (
        Product.objects.filter(parent=None)
        .annotate(average_cost=Avg("stocks__unit_cost"))
        .annotate(watchers_count=Count("watchers"))
        .order_by("remaining_qty", "title")
    )

    view_name = "N/A"

    if view == "in_stock" or (view != "out_of_stock" and view != "inactive"):
        # Get active products with remaining stocks
        products = products.filter(active=True, remaining_qty__gt=0)
        view_name = "In-Stock"
        return render(
        request,
        "shoppingwonder/stocks.html",
        {"products": products, "view_name": view_name},
        )

    if view == "out_of_stock":
        # Get active products with zero remaining stock or none
        products = products.filter(active=True).filter(
            Q(remaining_qty__lte=0) | Q(remaining_qty__isnull=True)
        )
        view_name = "Out-of-Stock"

    if view == "inactive":
        products = products.filter(active=False)
        view_name = "Inactive"

    return render(
        request,
        "shoppingwonder/stocks.html",
        {"products": products, "view_name": view_name},
    )


@staff_member_required
def sales(request):
    # Get the GET parameter
    view = request.GET.get("v")

    # Get all SOs
    latest_so_status = SalesOrderStatus.objects.filter(sales_order=OuterRef('sales_order')).order_by('-modified')[:1]
    so_statuses = SalesOrderStatus.objects.filter(id__in=Subquery(latest_so_status.values('id'))).order_by('-sales_order')
    view_name = "All"

    if view == "to_pay":
        # Filter status 1 ordered
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.ORDERED)
        view_name = "To Pay"

    if view == "to_ship":
        # Filter status 2 paid
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.PAID)
        view_name = "To Ship"

    if view == "to_receive":
        # Filter status 3 shipped
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.SHIPPED)
        view_name = "To Receive"

    if view == "received":
        # Filter status 4 delivered
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.DELIVERED)
        view_name = "Completed"

    # Pagination 9 orders/page
    p = Paginator(so_statuses, 9)

    # Display the first page
    page = p.page(1)

    # Get the GET parameter "p"
    try:
        page_num = int(request.GET.get("p"))

        # If there's get parameter and in the page range, display the requested page
        page = p.page(page_num)

    except:
        pass

    return render(
        request,
        "shoppingwonder/sales.html",
        {"so_statuses": page.object_list, "view_name": view_name, "Status": SalesOrderStatus.Status, "page": page},
    )


@login_required(login_url="login")
def purchases(request):
    # Get the GET parameter
    view = request.GET.get("v")

    # Get all SOs with the user as customer
    latest_so_status = SalesOrderStatus.objects.filter(sales_order__customer=request.user, sales_order=OuterRef('sales_order')).order_by('-modified')[:1]
    so_statuses = SalesOrderStatus.objects.filter(id__in=Subquery(latest_so_status.values('id'))).order_by('-sales_order')
    view_name = "All"

    if view == "to_pay":
        # Filter status 1 ordered
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.ORDERED)
        view_name = "To Pay"

    if view == "to_ship":
        # Filter status 2 paid
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.PAID)
        view_name = "To Ship"

    if view == "to_receive":
        # Filter status 3 shipped
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.SHIPPED)
        view_name = "To Receive"

    if view == "received":
        # Filter status 4 delivered
        so_statuses = so_statuses.filter(status=SalesOrderStatus.Status.DELIVERED)
        view_name = "Completed"

    # Pagination 9 orders/page
    p = Paginator(so_statuses, 9)

    # Display the first page
    page = p.page(1)

    # Get the GET parameter "p"
    try:
        page_num = int(request.GET.get("p"))

        # If there's get parameter and in the page range, display the requested page
        page = p.page(page_num)

    except:
        pass

    return render(
        request,
        "shoppingwonder/purchases.html",
        {"so_statuses": page.object_list, "view_name": view_name, "Status": SalesOrderStatus.Status, "page": page},
    )


@csrf_exempt
@staff_member_required
def paid(request):
    if request.method == "POST":
        # Get sales order pk from form
        so_num = request.POST["so_num"]

        # Get sales order instance
        sales_order = SalesOrder.objects.get(pk=so_num)

        # Create a paid status for the sales order
        if sales_order.get_so_status() == SalesOrderStatus.Status.ORDERED:
            create_so_status = SalesOrderStatus(sales_order=sales_order, status=SalesOrderStatus.Status.PAID)
            create_so_status.save()
    return HttpResponseRedirect(reverse("sales") + "?v=to_ship")


@csrf_exempt
@staff_member_required
def shipped(request):
    if request.method == "POST":
        # Get sales order pk from form
        so_num = request.POST["so_num"]

        # Get sales order instance
        sales_order = SalesOrder.objects.get(pk=so_num)

        # Create a shipped status for the sales order
        if sales_order.get_so_status() == SalesOrderStatus.Status.PAID:
            create_so_status = SalesOrderStatus(sales_order=sales_order, status=SalesOrderStatus.Status.SHIPPED)
            create_so_status.save()
    return HttpResponseRedirect(reverse("sales") + "?v=to_receive")


@csrf_exempt
@login_required(login_url="login")
def delivered(request):
    if request.method == "POST":
        # Get sales order pk from form
        so_num = request.POST["so_num"]

        # Get sales order instance
        sales_order = SalesOrder.objects.get(pk=so_num)

        # Create a delivered status for the sales order
        if sales_order.get_so_status() == SalesOrderStatus.Status.SHIPPED:
            create_so_status = SalesOrderStatus(sales_order=sales_order, status=SalesOrderStatus.Status.DELIVERED)
            create_so_status.save()

    return HttpResponseRedirect(reverse("purchases") + "?v=received")


