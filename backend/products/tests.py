import pytest
from products.models import Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(name="Usługi", slug="uslugi")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        category=category,
        name="Strona WWW",
        slug="strona-www",
        price="1500.00",
        is_active=True,
    )


@pytest.fixture
def inactive_product(db, category):
    return Product.objects.create(
        category=category,
        name="Stary produkt",
        slug="stary-produkt",
        price="500.00",
        is_active=False,
    )


@pytest.mark.django_db
class TestCategoryAPI:
    url = "/api/categories/"

    def test_list_categories_public(self, api_client, category):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_retrieve_category_by_slug(self, api_client, category):
        response = api_client.get(f"{self.url}{category.slug}/")
        assert response.status_code == 200
        assert response.data["name"] == "Usługi"

    def test_create_category_admin(self, admin_client):
        response = admin_client.post(self.url, {"name": "Grafika", "slug": "grafika"})
        assert response.status_code == 201
        assert Category.objects.filter(slug="grafika").exists()

    def test_create_category_forbidden_for_user(self, user_client):
        response = user_client.post(self.url, {"name": "Grafika", "slug": "grafika"})
        assert response.status_code == 403

    def test_create_category_forbidden_anonymous(self, api_client):
        response = api_client.post(self.url, {"name": "Grafika", "slug": "grafika"})
        assert response.status_code == 403

    def test_delete_category_admin(self, admin_client, category):
        response = admin_client.delete(f"{self.url}{category.slug}/")
        assert response.status_code == 204

    def test_delete_category_forbidden_for_user(self, user_client, category):
        response = user_client.delete(f"{self.url}{category.slug}/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestProductAPI:
    url = "/api/products/"

    def test_list_products_public(self, api_client, product):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_inactive_product_hidden_from_public(self, api_client, product, inactive_product):
        response = api_client.get(self.url)
        slugs = [p["slug"] for p in response.data["results"]]
        assert "stary-produkt" not in slugs

    def test_admin_sees_inactive_products(self, admin_client, product, inactive_product):
        response = admin_client.get(self.url)
        slugs = [p["slug"] for p in response.data["results"]]
        assert "stary-produkt" in slugs

    def test_retrieve_product_by_slug(self, api_client, product):
        response = api_client.get(f"{self.url}{product.slug}/")
        assert response.status_code == 200
        assert response.data["name"] == "Strona WWW"

    def test_filter_by_category(self, api_client, product, category):
        response = api_client.get(f"{self.url}?category={category.slug}")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_search_products(self, api_client, product):
        response = api_client.get(f"{self.url}?search=Strona")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_search_no_results(self, api_client, product):
        response = api_client.get(f"{self.url}?search=xyz_nieistnieje")
        assert response.status_code == 200
        assert len(response.data["results"]) == 0

    def test_create_product_admin(self, admin_client, category):
        data = {
            "category": category.pk,
            "name": "Logo",
            "slug": "logo",
            "price": "800.00",
            "is_active": True,
        }
        response = admin_client.post(self.url, data)
        assert response.status_code == 201

    def test_create_product_forbidden_for_user(self, user_client, category):
        data = {
            "category": category.pk,
            "name": "Logo",
            "slug": "logo",
            "price": "800.00",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 403

    def test_update_product_admin(self, admin_client, product):
        response = admin_client.patch(f"{self.url}{product.slug}/", {"price": "2000.00"})
        assert response.status_code == 200

    def test_delete_product_admin(self, admin_client, product):
        response = admin_client.delete(f"{self.url}{product.slug}/")
        assert response.status_code == 204

    def test_ordering_by_price(self, api_client, category):
        Product.objects.create(name="Tani", slug="tani", price="100.00", category=category, is_active=True)
        Product.objects.create(name="Drogi", slug="drogi", price="9000.00", category=category, is_active=True)
        response = api_client.get(f"{self.url}?ordering=price")
        assert response.status_code == 200
        prices = [p["price"] for p in response.data["results"]]
        assert prices == sorted(prices)
