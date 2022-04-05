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
from django.db.models import Sum, Avg, Count, Q
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import render_to_string

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

        # Get last 3 of products created
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
                CreateProduct = CartItem(shopper=request.user, product=product, quantity=1)
                CreateProduct.save()
                return get_cart_response(request)

            return JsonResponse({}, status=400)

    except ObjectDoesNotExist:
        return JsonResponse({}, status=400)


def get_cart_response(request):
    context = user_cart(request)
    cart_page = render_to_string("shoppingwonder/cart.html", context)
    cart_count = context["cart_count"]
    return JsonResponse({"cartPage": cart_page, "cartCount": cart_count})


@staff_member_required
def stocks(request):
    # Get the GET parameter
    view = request.GET.get("v")
    parents = Product.objects.filter(parent=None).order_by("title")

    children = (
        Product.objects.exclude(variations__value="Parent")
        .annotate(average_cost=Avg("stocks__unit_cost"))
        .annotate(remaining_qty=Sum("stocks__available_for_sales"))
        .annotate(watchers_count=Count("watchers"))
        .order_by("remaining_qty", "title")
    )

    if view is "in_stock":
        # Get active products with remaining stocks
        products = products.filter(active=True, remaining_qty__gt=0)

    if view is "out_of_stock":
        # Get active products that are not Parent with zero or none remaining stocks
        products = products.filter(active=True).filter(
            Q(remaining_qty__lte=0) | Q(remaining_qty__isnull=True)
        )

    if view is "inactive":
        products = products.filter(active=False)

    # for product in products:
    #     product.name
    #     product.variations.first()
    #     image = product.images.first()

    return render(
        request,
        "shoppingwonder/stock.html",
        {"stocks": stocks},
    )
