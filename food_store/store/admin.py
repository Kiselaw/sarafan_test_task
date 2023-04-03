from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Product,
    ProductImage,
    Subcategory,
)


class SubcategoryInline(admin.StackedInline):
    model = Subcategory
    show_change_link = True


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    show_change_link = True


class CartItemInline(admin.StackedInline):
    model = CartItem
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
    ]
    list_display = (
        "id",
        "name",
        "price",
        "brand",
        "description",
        "subcategory",
        "in_stock",
    )
    search_fields = ("name", "brand", "subcategory")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "image",
    )
    search_fields = ("product",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        SubcategoryInline,
    ]
    list_display = ("id", "name", "slug", "image")
    list_filter = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "slug", "image")
    list_filter = ("name",)
    search_fields = ("name", "category")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInline,
    ]
    list_display = (
        "id",
        "user",
    )
    list_filter = ("user",)
    search_fields = ("user",)


@admin.register(CartItem)
class CartItem(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product",
    )
    list_filter = ("cart",)
    search_fields = ("cart", "product")
