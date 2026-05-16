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

    def test_create_product_forbidden_anonymous(self, api_client, category):
        data = {"category": category.pk, "name": "X", "slug": "x", "price": "100.00"}
        response = api_client.post(self.url, data)
        assert response.status_code == 403

    def test_delete_product_forbidden_for_user(self, user_client, product):
        response = user_client.delete(f"{self.url}{product.slug}/")
        assert response.status_code == 403

    def test_delete_product_forbidden_anonymous(self, api_client, product):
        response = api_client.delete(f"{self.url}{product.slug}/")
        assert response.status_code == 403

    def test_delete_nonexistent_product(self, admin_client):
        response = admin_client.delete(f"{self.url}nie-istnieje/")
        assert response.status_code == 404

    def test_retrieve_inactive_product_anonymous(self, api_client, inactive_product):
        response = api_client.get(f"{self.url}{inactive_product.slug}/")
        assert response.status_code == 404

    def test_admin_can_retrieve_inactive_product(self, admin_client, inactive_product):
        response = admin_client.get(f"{self.url}{inactive_product.slug}/")
        assert response.status_code == 200
        assert response.data["is_active"] is False

    def test_update_product_forbidden_for_user(self, user_client, product):
        response = user_client.patch(f"{self.url}{product.slug}/", {"price": "9999.00"})
        assert response.status_code == 403

    def test_update_product_forbidden_anonymous(self, api_client, product):
        response = api_client.patch(f"{self.url}{product.slug}/", {"price": "9999.00"})
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminProductCRUD:
    """Testy operacji CRUD wykonywanych z poziomu zakładki Produkty w panelu admina."""

    url = "/api/products/"

    def test_create_with_description(self, admin_client, category):
        data = {
            "category": category.pk,
            "name": "Pełny produkt",
            "slug": "pelny-produkt",
            "description": "Szczegółowy opis produktu.",
            "price": "1200.00",
            "is_active": True,
        }
        response = admin_client.post(self.url, data)
        assert response.status_code == 201
        assert response.data["description"] == "Szczegółowy opis produktu."

    def test_create_inactive_product(self, admin_client, category):
        data = {
            "category": category.pk,
            "name": "Ukryty produkt",
            "slug": "ukryty-produkt",
            "price": "500.00",
            "is_active": False,
        }
        response = admin_client.post(self.url, data)
        assert response.status_code == 201
        assert response.data["is_active"] is False

    def test_create_duplicate_slug_rejected(self, admin_client, category, product):
        data = {
            "category": category.pk,
            "name": "Inny produkt",
            "slug": product.slug,
            "price": "999.00",
        }
        response = admin_client.post(self.url, data)
        assert response.status_code == 400

    def test_create_missing_required_fields(self, admin_client, category):
        response = admin_client.post(self.url, {"category": category.pk})
        assert response.status_code == 400

    def test_toggle_active_to_inactive(self, admin_client, product):
        assert product.is_active is True
        response = admin_client.patch(f"{self.url}{product.slug}/", {"is_active": False})
        assert response.status_code == 200
        assert response.data["is_active"] is False
        product.refresh_from_db()
        assert product.is_active is False

    def test_toggle_inactive_to_active(self, admin_client, inactive_product):
        assert inactive_product.is_active is False
        response = admin_client.patch(f"{self.url}{inactive_product.slug}/", {"is_active": True})
        assert response.status_code == 200
        assert response.data["is_active"] is True
        inactive_product.refresh_from_db()
        assert inactive_product.is_active is True

    def test_update_price(self, admin_client, product):
        response = admin_client.patch(f"{self.url}{product.slug}/", {"price": "2500.00"})
        assert response.status_code == 200
        assert response.data["price"] == "2500.00"
        product.refresh_from_db()
        assert str(product.price) == "2500.00"

    def test_update_name(self, admin_client, product):
        response = admin_client.patch(f"{self.url}{product.slug}/", {"name": "Zmieniona nazwa"})
        assert response.status_code == 200
        assert response.data["name"] == "Zmieniona nazwa"

    def test_update_category(self, admin_client, product, db):
        new_cat = Category.objects.create(name="Nowa kategoria", slug="nowa-kategoria")
        response = admin_client.patch(f"{self.url}{product.slug}/", {"category": new_cat.pk})
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.category == new_cat

    def test_update_slug(self, admin_client, product):
        response = admin_client.patch(f"{self.url}{product.slug}/", {"slug": "nowy-slug"})
        assert response.status_code == 200
        assert response.data["slug"] == "nowy-slug"
        assert Product.objects.filter(slug="nowy-slug").exists()
        assert not Product.objects.filter(slug=product.slug).exists()

    def test_delete_removes_from_db(self, admin_client, product):
        response = admin_client.delete(f"{self.url}{product.slug}/")
        assert response.status_code == 204
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_retrieve_contains_category_name(self, admin_client, category, product):
        response = admin_client.get(f"{self.url}{product.slug}/")
        assert response.status_code == 200
        assert "category_name" in response.data
        assert response.data["category_name"] == category.name


@pytest.mark.django_db
class TestCategoryAdminCRUD:
    """Testy operacji admina na kategoriach (używane w select formularza produktu)."""

    url = "/api/categories/"

    def test_update_category_admin(self, admin_client, category):
        response = admin_client.patch(f"{self.url}{category.slug}/", {"name": "Zmieniona"})
        assert response.status_code == 200
        assert response.data["name"] == "Zmieniona"

    def test_update_category_forbidden_for_user(self, user_client, category):
        response = user_client.patch(f"{self.url}{category.slug}/", {"name": "Zmieniona"})
        assert response.status_code == 403

    def test_update_category_forbidden_anonymous(self, api_client, category):
        response = api_client.patch(f"{self.url}{category.slug}/", {"name": "Zmieniona"})
        assert response.status_code == 403

    def test_retrieve_nonexistent_category(self, api_client):
        response = api_client.get(f"{self.url}nie-istnieje/")
        assert response.status_code == 404

    def test_create_category_duplicate_slug(self, admin_client, category):
        response = admin_client.post(self.url, {"name": "Inna", "slug": category.slug})
        assert response.status_code == 400


@pytest.mark.django_db
class TestProductOrderingDescending:
    url = "/api/products/"

    def test_ordering_by_price_descending(self, api_client, category):
        Product.objects.create(name="Tani", slug="tani", price="100.00", category=category, is_active=True)
        Product.objects.create(name="Drogi", slug="drogi", price="9000.00", category=category, is_active=True)
        Product.objects.create(name="Sredni", slug="sredni", price="500.00", category=category, is_active=True)
        response = api_client.get(f"{self.url}?ordering=-price")
        assert response.status_code == 200
        prices = [p["price"] for p in response.data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_ordering_by_name_ascending(self, api_client, category):
        Product.objects.create(name="Zebra", slug="zebra", price="100.00", category=category, is_active=True)
        Product.objects.create(name="Alfa", slug="alfa", price="200.00", category=category, is_active=True)
        response = api_client.get(f"{self.url}?ordering=name")
        assert response.status_code == 200
        names = [p["name"] for p in response.data["results"]]
        assert names == sorted(names)


@pytest.mark.django_db
class TestProductPagination:
    url = "/api/products/"

    def test_list_response_has_results_key(self, api_client, product):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data

    def test_category_list_has_results_key(self, api_client, category):
        response = api_client.get("/api/categories/")
        assert response.status_code == 200
        assert "results" in response.data


@pytest.mark.django_db
class TestCategoryDefaultOrdering:
    url = "/api/categories/"

    def test_categories_ordered_by_name(self, api_client, db):
        Category.objects.create(name="Zebra", slug="zebra")
        Category.objects.create(name="Alfa", slug="alfa")
        Category.objects.create(name="Marka", slug="marka")
        response = api_client.get(self.url)
        assert response.status_code == 200
        names = [c["name"] for c in response.data["results"]]
        assert names == sorted(names)
