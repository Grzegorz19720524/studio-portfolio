import pytest
from orders.models import Order, OrderItem
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
        name="Stary",
        slug="stary",
        price="100.00",
        is_active=False,
    )


@pytest.fixture
def order(db, regular_user, product):
    o = Order.objects.create(user=regular_user)
    OrderItem.objects.create(order=o, product=product, quantity=1, unit_price=product.price)
    o.recalculate_total()
    return o


@pytest.mark.django_db
class TestOrderCreate:
    url = "/api/orders/"

    def test_create_order_authenticated(self, user_client, product):
        data = {"items": [{"product": product.pk, "quantity": 2}]}
        response = user_client.post(self.url, data, format="json")
        assert response.status_code == 201
        assert Order.objects.count() == 1
        assert response.data["total"] == "3000.00"

    def test_create_order_anonymous(self, api_client, product):
        data = {"items": [{"product": product.pk, "quantity": 1}]}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 403

    def test_create_order_empty_items(self, user_client):
        response = user_client.post(self.url, {"items": []}, format="json")
        assert response.status_code == 400

    def test_create_order_inactive_product(self, user_client, inactive_product):
        data = {"items": [{"product": inactive_product.pk, "quantity": 1}]}
        response = user_client.post(self.url, data, format="json")
        assert response.status_code == 400

    def test_total_calculated_correctly(self, user_client, product):
        data = {"items": [{"product": product.pk, "quantity": 3}]}
        response = user_client.post(self.url, data, format="json")
        assert response.status_code == 201
        assert response.data["total"] == "4500.00"


@pytest.mark.django_db
class TestOrderList:
    url = "/api/orders/"

    def test_user_sees_own_orders_only(self, user_client, order, admin_user, product):
        other_order = Order.objects.create(user=admin_user)
        OrderItem.objects.create(order=other_order, product=product, quantity=1, unit_price=product.price)
        response = user_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_admin_sees_all_orders(self, admin_client, order):
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestOrderRetrieve:
    def test_user_can_retrieve_own_order(self, user_client, order):
        response = user_client.get(f"/api/orders/{order.pk}/")
        assert response.status_code == 200
        assert response.data["id"] == order.pk

    def test_user_cannot_retrieve_other_order(self, admin_client, order, api_client, regular_user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username="other", password="pass123!")
        from rest_framework.test import APIClient
        other_client = APIClient()
        other_client.force_login(other)
        response = other_client.get(f"/api/orders/{order.pk}/")
        assert response.status_code == 404

    def test_admin_can_retrieve_any_order(self, admin_client, order):
        response = admin_client.get(f"/api/orders/{order.pk}/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrderStatus:
    def test_admin_can_change_status(self, admin_client, order):
        response = admin_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "confirmed"},
            format="json",
        )
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == "confirmed"

    def test_user_cannot_change_status(self, user_client, order):
        response = user_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "confirmed"},
            format="json",
        )
        assert response.status_code == 403

    def test_anonymous_cannot_change_status(self, api_client, order):
        response = api_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "confirmed"},
            format="json",
        )
        assert response.status_code == 403

    def test_invalid_status_rejected(self, admin_client, order):
        response = admin_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "nieistnieje"},
            format="json",
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("new_status", [
        "pending", "confirmed", "in_progress", "completed", "cancelled",
    ])
    def test_all_valid_statuses_accepted(self, admin_client, order, new_status):
        response = admin_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": new_status},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == new_status

    def test_status_display_returned_after_change(self, admin_client, order):
        response = admin_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "in_progress"},
            format="json",
        )
        assert response.status_code == 200
        assert "status_display" in response.data
        assert response.data["status_display"] != ""

    def test_status_change_updates_db(self, admin_client, order):
        admin_client.patch(
            f"/api/orders/{order.pk}/status/",
            {"status": "completed"},
            format="json",
        )
        order.refresh_from_db()
        assert order.status == "completed"


@pytest.mark.django_db
class TestOrderDelete:
    def test_admin_can_delete_order(self, admin_client, order):
        response = admin_client.delete(f"/api/orders/{order.pk}/")
        assert response.status_code == 204

    def test_user_cannot_delete_order(self, user_client, order):
        response = user_client.delete(f"/api/orders/{order.pk}/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestOrderItemModel:
    def test_subtotal_single_item(self, db, regular_user, product):
        from decimal import Decimal
        o = Order.objects.create(user=regular_user)
        item = OrderItem.objects.create(order=o, product=product, quantity=3, unit_price=Decimal("100.00"))
        assert item.subtotal == Decimal("300.00")

    def test_subtotal_quantity_one(self, db, regular_user, product):
        from decimal import Decimal
        o = Order.objects.create(user=regular_user)
        item = OrderItem.objects.create(order=o, product=product, quantity=1, unit_price=Decimal("1500.00"))
        assert item.subtotal == Decimal("1500.00")

    def test_recalculate_total_single_item(self, order):
        from decimal import Decimal
        order.recalculate_total()
        order.refresh_from_db()
        assert order.total == Decimal("1500.00")

    def test_recalculate_total_after_adding_item(self, db, regular_user, product, category):
        second = Product.objects.create(
            category=category, name="Logo", slug="logo", price="500.00", is_active=True,
        )
        o = Order.objects.create(user=regular_user)
        OrderItem.objects.create(order=o, product=product, quantity=1, unit_price=product.price)
        OrderItem.objects.create(order=o, product=second, quantity=2, unit_price=second.price)
        o.recalculate_total()
        o.refresh_from_db()
        from decimal import Decimal
        assert o.total == Decimal("2500.00")

    def test_unit_price_set_from_product_price(self, user_client, product):
        data = {"items": [{"product": product.pk, "quantity": 1}]}
        response = user_client.post("/api/orders/", data, format="json")
        assert response.status_code == 201
        order = Order.objects.get(pk=response.data["id"])
        item = order.items.first()
        from decimal import Decimal
        assert item.unit_price == Decimal(product.price)


@pytest.mark.django_db
class TestOrderMultiItem:
    url = "/api/orders/"

    def test_create_order_multiple_products(self, user_client, product, category):
        second = Product.objects.create(
            category=category, name="Logo", slug="logo", price="800.00", is_active=True,
        )
        data = {
            "items": [
                {"product": product.pk, "quantity": 1},
                {"product": second.pk, "quantity": 2},
            ]
        }
        response = user_client.post(self.url, data, format="json")
        assert response.status_code == 201
        from decimal import Decimal
        # 1×1500 + 2×800 = 3100
        assert Decimal(response.data["total"]) == Decimal("3100.00")

    def test_multi_item_order_item_count(self, user_client, product, category):
        second = Product.objects.create(
            category=category, name="Logo2", slug="logo2", price="200.00", is_active=True,
        )
        data = {
            "items": [
                {"product": product.pk, "quantity": 1},
                {"product": second.pk, "quantity": 1},
            ]
        }
        response = user_client.post(self.url, data, format="json")
        assert response.status_code == 201
        order = Order.objects.get(pk=response.data["id"])
        assert order.items.count() == 2


@pytest.mark.django_db
class TestOrderDefaultOrdering:
    url = "/api/orders/"

    def test_orders_returned_newest_first(self, user_client, regular_user, product):
        import time
        o1 = Order.objects.create(user=regular_user)
        OrderItem.objects.create(order=o1, product=product, quantity=1, unit_price=product.price)
        time.sleep(0.01)
        o2 = Order.objects.create(user=regular_user)
        OrderItem.objects.create(order=o2, product=product, quantity=1, unit_price=product.price)
        response = user_client.get(self.url)
        assert response.status_code == 200
        ids = [r["id"] for r in response.data["results"]]
        assert ids[0] == o2.pk


@pytest.mark.django_db
class TestOrderPagination:
    url = "/api/orders/"

    def test_list_response_has_results_key(self, user_client, order):
        response = user_client.get(self.url)
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
