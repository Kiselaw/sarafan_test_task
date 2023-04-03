from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=150, unique=True, blank=False, null=False
    )
    slug = models.SlugField(unique=True, blank=False, null=False)
    image = models.ImageField(upload_to="images/categories/")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Subcategory(models.Model):
    name = models.CharField(
        max_length=150, unique=True, blank=False, null=False
    )
    slug = models.SlugField(unique=True, blank=False, null=False)
    category = models.ForeignKey(
        Category, related_name="subcategories", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="images/subcategories/")

    class Meta:
        verbose_name_plural = "Subcategories"

    def __str__(self) -> str:
        return f"{self.category.name}:{self.name}"


class Product(models.Model):
    name = models.CharField(
        max_length=150, unique=True, blank=False, null=False
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=False,
        null=False,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )
    brand = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    slug = models.SlugField(unique=True, blank=False, null=False)
    subcategory = models.ForeignKey(
        Subcategory, related_name="products", on_delete=models.CASCADE
    )
    in_stock = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="images/products")

    def __str__(self) -> str:
        return f"{self.product}:{self.id}"


class Cart(models.Model):
    user = models.ForeignKey(
        User, related_name="cart", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.id}:{self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, related_name="cart_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="cart_item", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.cart}:{self.product}"
