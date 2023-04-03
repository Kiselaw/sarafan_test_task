from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from store.models import (
    Cart,
    CartItem,
    Category,
    Product,
    ProductImage,
    Subcategory,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {"password": {"write_only": True}}


class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = ("image", "product")
        model = ProductImage


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(max_length=150, allow_empty_file=False),
        write_only=True,
        required=False,
    )
    category = serializers.SerializerMethodField()
    subcategory = serializers.SlugRelatedField(
        queryset=Subcategory.objects.all(), slug_field="name"
    )

    class Meta:
        fields = "__all__"
        model = Product
        read_only_fields = ("upload_images",)

    def create(self, validated_data):
        try:
            images = validated_data.pop("upload_images")
            product = Product.objects.create(**validated_data)
            for image in images:
                ProductImage.objects.create(product=product, image=image)
        except KeyError:
            product = Product.objects.create(**validated_data)
        product.save()
        return product

    def get_category(self, obj):
        return obj.subcategory.category.name

    def validate_price(self, value):
        if value < Decimal("0.01"):
            raise serializers.ValidationError(
                "Price can not be less than 0.01."
            )
        return value


class SubcategorySerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name"
    )
    image = serializers.ImageField(required=False)

    class Meta:
        fields = "__all__"
        model = Subcategory


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        fields = "__all__"
        model = Category


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        fields = ("product", "price", "quantity")
        model = CartItem
        read_only_fields = ("product", "cart")

    def get_price(self, obj):
        return obj.product.price

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity can not be less than 1."
            )
        return value


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Cart
