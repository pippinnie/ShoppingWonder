from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("stocks", views.stocks, name="stocks"),
    path("contact", views.contact, name="contact"),
    path("profile", views.profile, name="profile"),
    path("product/<int:parent_id>", views.product, name="product"),
    path("product/<int:parent_id>/toggle-fav", views.toggle_fav, name="toggle_fav"),
    path("fav", views.favorites, name="favorites"),
    path("cart/<int:product_id>/<str:action>", views.cart, name="cart"),
    path("order", views.order, name="order"),
    path("purchases", views.purchases, name="purchases"),
    path("delivered", views.delivered, name="delivered"),
    path("sales", views.sales, name="sales"),
    path("paid", views.paid, name="paid"),
    path("shipped", views.shipped, name="shipped"),
]