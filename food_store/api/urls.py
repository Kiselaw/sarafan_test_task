from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (CartItemViewSet, CartViewSet, CategoryViewSet,
                    ProductViewSet, SubcategoryViewSet, UserViewSet)

app_name = "api"

router = DefaultRouter()

router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("subcategories", SubcategoryViewSet, basename="subcategory")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("users/me/", UserViewSet.as_view({"get": "get"}), name="user-detail"),
    path(
        "shopping-cart/",
        CartViewSet.as_view({"get": "get"}),
        name="cart-detail",
    ),
    path(
        "shopping-cart/clear/",
        CartViewSet.as_view({"post": "clear_cart"}),
        name="cart-clear",
    ),
    path(
        "shopping-cart/num-items-and-total/",
        CartViewSet.as_view({"get": "count_and_total"}),
        name="cart-count-total",
    ),
    path(
        "products/<int:product_id>/shopping-cart/",
        CartItemViewSet.as_view(
            {"post": "create", "delete": "destroy", "patch": "partial_update"}
        ),
        name="add-item",
    ),
    path("token-auth/", views.obtain_auth_token),
]
