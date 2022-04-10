from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from martor.models import MartorField
from django.contrib import admin
from django.db.models import Avg
from decimal import Decimal

# Create your models here.
class User(AbstractUser):
    pass


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    value = models.CharField(max_length=64)
    attribute = models.ForeignKey(
        Attribute, related_name="attribute_value", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.value


class Product(models.Model):
    title = models.CharField(max_length=64)
    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, null=True, blank=True
    )
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    variations = models.ManyToManyField(
        AttributeValue, related_name="products", blank=True
    )
    RSP = models.DecimalField(
        decimal_places=2, max_digits=6, validators=[MinValueValidator(0.0)]
    )
    watchers = models.ManyToManyField(User, related_name="favorites", blank=True)
    minQty = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    remaining_qty = models.PositiveIntegerField(default=0)
    sold = models.PositiveBigIntegerField(default=0)
    views = models.PositiveBigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    details = MartorField(blank=True)

    def __str__(self):
        return f"{self.id} | {self.title}"

    def adjust_qty(self, qty):
        # Update product remaining qty
        self.remaining_qty += qty
        self.save()

        # Update parent product remaining qty if any
        if self.parent:
            self.parent.remaining_qty += qty
            self.parent.save()

    def adjust_sold(self, qty):
        # Update product sold qty
        self.sold += qty
        self.save()

        # Update parent product sold qty if any
        if self.parent:
            self.parent.sold += qty
            self.parent.save()

    def is_sellable(self):
        return self.active and (self.remaining_qty > 0)


class Image(models.Model):
    imageURL = models.URLField(max_length=1024)
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.product)


class Stock(models.Model):
    product = models.ForeignKey(
        Product, related_name="stocks", on_delete=models.CASCADE
    )
    unit_cost = models.DecimalField(
        decimal_places=2, max_digits=6, validators=[MinValueValidator(0.0)]
    )
    quantity = models.PositiveIntegerField()
    available_for_sales = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.product)


class Price(models.Model):
    product = models.ForeignKey(
        Product, related_name="prices", on_delete=models.CASCADE
    )
    price = models.DecimalField(
        decimal_places=2, max_digits=6, validators=[MinValueValidator(0.0)]
    )
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return str(self.product)


class CartItem(models.Model):
    class Meta:
        unique_together = [['shopper', 'product']]

    shopper = models.ForeignKey(User, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="cart_items", on_delete=models.CASCADE, null=True
    )
    quantity = models.PositiveIntegerField()
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shopper} | {self.product} | Qty: {self.quantity}"

    def get_amount(self):
        return self.quantity * self.product.RSP


class SalesOrder(models.Model):
    customer = models.ForeignKey(
        User, related_name="sales_orders", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(
        Product, related_name="sales_orders", through="SalesOrderLineItem"
    )
    amount = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(0.0)]
    )

    def __str__(self):
        return f"{self.id} | Customer: {self.customer}"

    def get_so_status(self):
        last_status =  self.sales_order_status.order_by("-modified").first()
        return last_status.status

    def get_total_cost(self):
        so_line_items = self.sales_order_line_items.all()
        total_cost = 0
        for so_line_item in so_line_items:
            subtotal_cost = so_line_item.get_cost()
            total_cost += subtotal_cost
        return total_cost

    def get_total_profit(self):
        return self.amount - self.get_total_cost()


class SalesOrderStatus(models.Model):
    class Meta:
        verbose_name_plural = "Sales order statuses"


    class Status(models.IntegerChoices):
        CANCELLED = 0
        ORDERED = 1
        PAID = 2
        SHIPPED = 3
        DELIVERED = 4

    sales_order = models.ForeignKey(
        SalesOrder, related_name="sales_order_status", on_delete=models.CASCADE
    )
    status = models.IntegerField(choices=Status.choices, default=Status.ORDERED)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_status_display()


class SalesOrderLineItem(models.Model):
    sales_order = models.ForeignKey(
        SalesOrder, related_name="sales_order_line_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="sales_order_line_items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        decimal_places=2, max_digits=6, validators=[MinValueValidator(0.0)]
    )
    stocks = models.ManyToManyField(Stock, related_name="sales_order_line_items")

    def __str__(self):
        return str(self.sales_order)

    def get_amount(self):
        return self.quantity * self.unit_price

    def get_avg_unit_cost(self):
        related_stock = self.stocks.aggregate(average_cost=Avg("unit_cost"))
        return related_stock["average_cost"]

    def get_cost(self):
        return self.quantity * self.get_avg_unit_cost()

    def get_profit(self):
        return self.get_amount() - self.get_cost()

