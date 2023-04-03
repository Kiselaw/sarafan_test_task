from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from store.models import Cart, CartItem, Category, Product, Subcategory

from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
    SubcategorySerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs) -> Response:
        user = User.objects.get(id=self.request.user.id)
        serialized_data = self.serializer_class(user).data
        return Response(serialized_data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [permissions.AllowAny]

    def get_serializer(self, *args, **kwargs) -> ProductSerializer:
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, list):
                kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class CategoryViewSet(ProductViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryViewSet(ProductViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs) -> Response:
        cart = Cart.objects.get_or_create(user=self.request.user)
        serialized_data = self.serializer_class(cart[0]).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    def clear_cart(self, *args, **kwargs) -> Response:
        cart = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart[0].cart_items.all()
        cart_items.delete()
        serialized_data = self.serializer_class(cart[0]).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    def count_and_total(self, *args, **kwargs) -> Response:
        cart = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart[0].cart_items.all()
        num_items = sum(item.quantity for item in cart_items)
        total = sum(item.product.price for item in cart_items)
        return Response({"num_items": num_items, "total": total})


class CartItemViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer) -> Response:
        cart = Cart.objects.get_or_create(user=self.request.user)
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, pk=product_id)
        if product.in_stock is False:
            raise ValidationError(
                {"error": "Product is out of stock."},
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer.save(cart=cart[0], product=product)
        except IntegrityError:
            raise ValidationError(
                {"error": "Product is already in the cart."},
                status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, *args, **kwargs) -> Response:
        product_id = self.kwargs.get("product_id")
        cart = Cart.objects.get(user=self.request.user)
        cart_item = CartItem.objects.get(cart=cart, product=product_id)
        cart_item.delete()
        return Response(
            {"success": "Product have been removed from the cart."},
            status=status.HTTP_204_NO_CONTENT,
        )

    def partial_update(self, *args, **kwargs) -> Response:
        product_id = self.kwargs.get("product_id")
        cart = Cart.objects.get(user=self.request.user)
        cart_item = CartItem.objects.get(cart=cart, product=product_id)
        quantity = self.request.data.get("quantity")
        if int(quantity) < 1:
            raise ValidationError(
                {"error": "Quantity can not be less than 1."},
                status.HTTP_400_BAD_REQUEST,
            )
        cart_item.quantity = quantity
        cart_item.save()
        serialized_data = self.serializer_class(cart_item).data
        return Response(serialized_data, status=status.HTTP_200_OK)
