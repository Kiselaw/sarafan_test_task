from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Product, Category, Subcategory, Cart, CartItem, User

from ..serializers import (
    ProductSerializer,
    CategorySerializer,
    SubcategorySerializer,
    CartSerializer,
    CartItemSerializer,
    UserSerializer,
)


class TestData(APITestCase):
    def setUp(self):
        self.category_1 = Category.objects.create(
            name="Category-1",
            slug="category-1",
        )
        self.category_2 = Category.objects.create(
            name="Category-2",
            slug="category-2",
        )
        self.subcategory_1 = Subcategory.objects.create(
            name="Subcategory-1",
            slug="subcategory-1",
            category=self.category_1,
        )
        self.subcategory_2 = Subcategory.objects.create(
            name="Subcategory-2",
            slug="subcategory-2",
            category=self.category_1,
        )
        self.product_1 = Product.objects.create(
            name="Product-1",
            price=10,
            brand="Brand-1",
            slug="product-1",
            in_stock=True,
            description="Description-1",
            subcategory=self.subcategory_1,
        )
        self.product_2 = Product.objects.create(
            name="Product-2",
            price=10,
            brand="Brand-2",
            slug="product-2",
            in_stock=True,
            description="Description-2",
            subcategory=self.subcategory_1,
        )
        self.product_3 = Product.objects.create(
            name="Product-3",
            price=10,
            brand="Brand-3",
            slug="product-3",
            in_stock=False,
            description="Description-3",
            subcategory=self.subcategory_1,
        )
        self.user = User.objects.create(
            username="test-user", password="test-password"
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product_1
        )


class ProductViewSetTestCase(TestData):
    def test_create_valid_product(self):
        url = reverse("api:product-list")
        data = {
            "name": "Product-4",
            "price": 10,
            "brand": "Brand-4",
            "slug": "product-4",
            "in_stock": True,
            "description": "Description-4",
            "subcategory": "Subcategory-1",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(name="Product-4")
        expected_data = ProductSerializer(product).data
        self.assertEqual(response.data, expected_data)

    def test_create_unvalid_product(self):
        url = reverse("api:product-list")
        data = {
            "name": "Product-5",
            "price": -10,
            "brand": "Brand-5",
            "slug": "product-5",
            "in_stock": True,
            "description": "Description-5",
            "subcategory": "Subcategory-1",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_products(self):
        url = reverse("api:product-list")
        data = [
            {
                "name": "Product-4",
                "price": 10,
                "brand": "Brand-4",
                "slug": "product-4",
                "in_stock": True,
                "description": "Description-4",
                "subcategory": "Subcategory-1",
            },
            {
                "name": "Product-5",
                "price": 10,
                "brand": "Brand-5",
                "slug": "product-5",
                "in_stock": True,
                "description": "Description-5",
                "subcategory": "Subcategory-1",
            },
        ]
        response = self.client.post(url, data, fopirmat="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 5)
        expected_data = ProductSerializer(
            Product.objects.filter(pk__in=[4, 5]), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_muptiple_products(self):
        url = reverse("api:product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProductSerializer(
            Product.objects.all(), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_certain_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProductSerializer(self.product_1).data
        self.assertEqual(response.data, expected_data)

    def test_valid_patch_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        data = {"price": 100}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_1.refresh_from_db()
        expected_data = ProductSerializer(self.product_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_patch_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        data = {"price": -100, "description": 42}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_put_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        data = {
            "name": "Product-1-new",
            "price": 100,
            "brand": "Brand-1-new",
            "slug": "slug-1-new",
            "in_stock": True,
            "description": "Description-1-new",
            "subcategory": "Subcategory-2",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_1.refresh_from_db()
        expected_data = ProductSerializer(self.product_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_put_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        data = {"price": 100, "description": 42}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_product(self):
        url = reverse("api:product-detail", kwargs={"pk": self.product_1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CategoryViewSetTestCase(TestData):
    def test_create_valid_category(self):
        url = reverse("api:category-list")
        data = {
            "name": "Category-3",
            "slug": "category-3",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(name="Category-3")
        expected_data = CategorySerializer(category).data
        self.assertEqual(response.data, expected_data)

    def test_create_unvalid_category(self):
        url = reverse("api:category-list")
        data = {
            "name": "",
            "slug": "category-3",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_categories(self):
        url = reverse("api:category-list")
        data = [
            {
                "name": "Category-3",
                "slug": "category-3",
            },
            {
                "name": "Category-4",
                "slug": "category-4",
            },
        ]
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 4)
        expected_data = CategorySerializer(
            Category.objects.filter(pk__in=[3, 4]), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_multiple_categories(self):
        url = reverse("api:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = CategorySerializer(
            Category.objects.all(), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_certain_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = CategorySerializer(self.category_1).data
        self.assertEqual(response.data, expected_data)

    def test_valid_patch_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        data = {"slug": "category-1-new"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_1.refresh_from_db()
        expected_data = CategorySerializer(self.category_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_patch_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        data = {"name": ""}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_put_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        data = {
            "name": "Category-1-new",
            "slug": "category-1-new",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_1.refresh_from_db()
        expected_data = CategorySerializer(self.category_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_put_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        data = {}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_category(self):
        url = reverse("api:category-detail", kwargs={"pk": self.category_1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubcategoryViewSetTestCase(TestData):
    def test_create_valid_subcategory(self):
        url = reverse("api:subcategory-list")
        data = {
            "name": "Subcategory-3",
            "slug": "subcategory-3",
            "category": "Category-1",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        subcategory = Subcategory.objects.get(name="Subcategory-3")
        expected_data = SubcategorySerializer(subcategory).data
        self.assertEqual(response.data, expected_data)

    def test_create_unvalid_subcategory(self):
        url = reverse("api:category-list")
        data = {"name": "", "slug": "subcategory-3", "category": "Category-1"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_subcategories(self):
        url = reverse("api:subcategory-list")
        data = [
            {
                "name": "Subcategory-3",
                "slug": "subcategory-3",
                "category": "Category-1",
            },
            {
                "name": "Subcategory-4",
                "slug": "subcategory-4",
                "category": "Category-1",
            },
        ]
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = SubcategorySerializer(
            Subcategory.objects.filter(pk__in=[3, 4]), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_multiple_subcategories(self):
        url = reverse("api:subcategory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = SubcategorySerializer(
            Subcategory.objects.all(), many=True
        ).data
        self.assertEqual(response.data, expected_data)

    def test_get_certain_subcategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = SubcategorySerializer(self.subcategory_1).data
        self.assertEqual(response.data, expected_data)

    def test_valid_patch_subcsategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        data = {"slug": "subcategory-1-new"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subcategory_1.refresh_from_db()
        expected_data = SubcategorySerializer(self.subcategory_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_patch_subcsategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        data = {"slug": ""}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_put_subcategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        data = {
            "name": "Subcategory-1-new",
            "slug": "Subcategory-1-new",
            "category": "Category-1",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subcategory_1.refresh_from_db()
        expected_data = SubcategorySerializer(self.subcategory_1).data
        self.assertEqual(response.data, expected_data)

    def test_unvalid_put_subcategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        data = {}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_subcategory(self):
        url = reverse(
            "api:subcategory-detail", kwargs={"pk": self.subcategory_1.pk}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CartViewSetTestCase(TestData):
    def test_get_cart(self):
        url = reverse("api:cart-detail")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        expected_data = CartSerializer(self.cart).data
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            expected_data,
        )

    def test_clear_cart(self):
        url = reverse("api:cart-clear")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.cart.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(self.cart.cart_items.count(), 0)

    def test_count_and_total(self):
        url = reverse("api:cart-count-total")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        expected_data = {"num_items": 1, "total": 10}
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            expected_data,
        )

    def test_restrict_unauthenticated_user(self):
        url = reverse("api:cart-detail")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class CartItemViewSetTestCase(TestData):
    def test_create_valid_cart_item(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_2.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 2)

    def test_create_out_of_stock_cart_item(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_3.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_cart_item(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_1.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_cart_item(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_1.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_update_cart_item_quantity(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_1.pk})
        self.client.force_authenticate(user=self.user)
        data = {"quantity": 10}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cart_item.refresh_from_db()
        expected_data = CartItemSerializer(self.cart_item).data
        self.assertEqual(response.data, expected_data)

    def test_update_invalid_cart_item_quantity(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_1.pk})
        self.client.force_authenticate(user=self.user)
        data = {"quantity": -10}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restrict_unauthenticated_user(self):
        url = reverse("api:add-item", kwargs={"product_id": self.product_2.pk})
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class UserViewSetTestCase(TestData):
    def test_get_user(self):
        url = reverse("api:user-detail")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = UserSerializer(self.user).data
        self.assertEqual(response.data, expected_data)
