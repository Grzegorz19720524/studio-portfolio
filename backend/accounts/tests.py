import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegister:
    url = "/api/auth/register/"

    def test_register_success(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 201
        assert User.objects.filter(username="newuser").exists()

    def test_register_password_mismatch(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass123!",
            "password2": "WrongPass123!",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 400

    def test_register_weak_password(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "123",
            "password2": "123",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 400

    def test_register_duplicate_username(self, api_client, regular_user):
        data = {
            "username": regular_user.username,
            "email": "other@test.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    url = "/api/auth/login/"

    def test_login_success(self, api_client, regular_user):
        response = api_client.post(self.url, {"username": "user", "password": "user123!"})
        assert response.status_code == 200
        assert response.data["username"] == "user"

    def test_login_wrong_password(self, api_client, regular_user):
        response = api_client.post(self.url, {"username": "user", "password": "wrong"})
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post(self.url, {"username": "ghost", "password": "pass"})
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogout:
    url = "/api/auth/logout/"

    def test_logout_authenticated(self, user_client):
        response = user_client.post(self.url)
        assert response.status_code == 200

    def test_logout_anonymous(self, api_client):
        response = api_client.post(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestMe:
    url = "/api/auth/me/"

    def test_get_profile(self, user_client, regular_user):
        response = user_client.get(self.url)
        assert response.status_code == 200
        assert response.data["username"] == regular_user.username

    def test_get_profile_anonymous(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_patch_profile(self, user_client):
        response = user_client.patch(self.url, {"phone": "123456789"})
        assert response.status_code == 200
        assert response.data["phone"] == "123456789"


@pytest.mark.django_db
class TestChangePassword:
    url = "/api/auth/change-password/"

    def test_change_password_success(self, user_client):
        data = {
            "old_password": "user123!",
            "new_password": "NewStrong456!",
            "new_password2": "NewStrong456!",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 200

    def test_change_password_wrong_old(self, user_client):
        data = {
            "old_password": "wrong",
            "new_password": "NewStrong456!",
            "new_password2": "NewStrong456!",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 400

    def test_change_password_mismatch(self, user_client):
        data = {
            "old_password": "user123!",
            "new_password": "NewStrong456!",
            "new_password2": "DifferentPass456!",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 400

    def test_change_password_anonymous(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminUsers:
    url = "/api/admin/users/"

    def test_admin_can_list_users(self, admin_client, regular_user):
        response = admin_client.get(self.url)
        assert response.status_code == 200
        usernames = [u["username"] for u in response.data["results"]]
        assert regular_user.username in usernames

    def test_regular_user_cannot_list(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == 403

    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_admin_can_retrieve_user(self, admin_client, regular_user):
        response = admin_client.get(f"{self.url}{regular_user.pk}/")
        assert response.status_code == 200
        assert response.data["username"] == regular_user.username
        assert response.data["email"] == regular_user.email

    def test_response_contains_expected_fields(self, admin_client, regular_user):
        response = admin_client.get(f"{self.url}{regular_user.pk}/")
        for field in ["id", "username", "email", "is_active", "is_staff", "created_at"]:
            assert field in response.data

    def test_admin_can_deactivate_user(self, admin_client, regular_user):
        url = f"{self.url}{regular_user.pk}/"
        response = admin_client.patch(url, {"is_active": False})
        assert response.status_code == 200
        assert response.data["is_active"] is False
        regular_user.refresh_from_db()
        assert regular_user.is_active is False

    def test_admin_can_activate_user(self, admin_client, regular_user):
        regular_user.is_active = False
        regular_user.save()
        response = admin_client.patch(f"{self.url}{regular_user.pk}/", {"is_active": True})
        assert response.status_code == 200
        assert response.data["is_active"] is True
        regular_user.refresh_from_db()
        assert regular_user.is_active is True

    def test_admin_can_update_user_fields(self, admin_client, regular_user):
        response = admin_client.patch(
            f"{self.url}{regular_user.pk}/",
            {"first_name": "Nowe", "last_name": "Nazwisko"},
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Nowe"
        assert response.data["last_name"] == "Nazwisko"

    def test_regular_user_cannot_retrieve(self, user_client, regular_user):
        response = user_client.get(f"{self.url}{regular_user.pk}/")
        assert response.status_code == 403

    def test_regular_user_cannot_patch(self, user_client, regular_user):
        response = user_client.patch(f"{self.url}{regular_user.pk}/", {"is_active": False})
        assert response.status_code == 403

    def test_retrieve_nonexistent_user(self, admin_client):
        response = admin_client.get(f"{self.url}99999/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestAdminStats:
    url = "/api/admin/stats/"

    def test_admin_can_access(self, admin_client):
        response = admin_client.get(self.url)
        assert response.status_code == 200

    def test_regular_user_forbidden(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == 403

    def test_anonymous_forbidden(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_response_structure(self, admin_client):
        response = admin_client.get(self.url)
        data = response.data
        assert "users" in data
        assert "orders" in data
        assert "products" in data
        assert "messages" in data

    def test_users_section(self, admin_client, regular_user):
        response = admin_client.get(self.url)
        users = response.data["users"]
        assert "total" in users
        assert "active" in users
        assert "staff" in users
        assert "new_30d" in users
        assert users["total"] >= 2  # admin + regular_user

    def test_orders_section(self, admin_client):
        response = admin_client.get(self.url)
        orders = response.data["orders"]
        assert "total" in orders
        assert "new_30d" in orders
        assert "by_status" in orders
        assert "revenue_completed" in orders

    def test_products_section(self, admin_client):
        response = admin_client.get(self.url)
        products = response.data["products"]
        assert "total" in products
        assert "active" in products
        assert "inactive" in products

    def test_messages_section(self, admin_client):
        response = admin_client.get(self.url)
        messages = response.data["messages"]
        assert "total" in messages
        assert "unread" in messages

    def test_counts_reflect_db_state(self, admin_client, db):
        from django.contrib.auth import get_user_model
        from orders.models import Order, OrderItem
        from products.models import Category, Product
        from contact.models import ContactMessage

        User = get_user_model()
        u = User.objects.create_user(username="stat_user", password="pass123!")
        cat = Category.objects.create(name="Kat", slug="kat")
        prod = Product.objects.create(name="P", slug="p", price="100.00", category=cat, is_active=True)
        order = Order.objects.create(user=u, status="completed")
        OrderItem.objects.create(order=order, product=prod, quantity=1, unit_price=prod.price)
        order.recalculate_total()
        ContactMessage.objects.create(name="X", email="x@x.pl", subject="S", message="M", is_read=False)

        response = admin_client.get(self.url)
        data = response.data
        assert data["orders"]["total"] >= 1
        assert data["orders"]["by_status"].get("completed", 0) >= 1
        assert float(data["orders"]["revenue_completed"]) >= 100.0
        assert data["products"]["total"] >= 1
        assert data["messages"]["unread"] >= 1

    def test_active_inactive_product_counts(self, admin_client, db):
        from products.models import Category, Product
        cat = Category.objects.create(name="C", slug="c")
        Product.objects.create(name="Aktywny", slug="aktywny", price="1.00", category=cat, is_active=True)
        Product.objects.create(name="Ukryty", slug="ukryty", price="1.00", category=cat, is_active=False)

        response = admin_client.get(self.url)
        products = response.data["products"]
        assert products["active"] >= 1
        assert products["inactive"] >= 1

    def test_unread_messages_count(self, admin_client, db):
        from contact.models import ContactMessage
        ContactMessage.objects.create(name="A", email="a@a.pl", subject="S", message="M", is_read=False)
        ContactMessage.objects.create(name="B", email="b@b.pl", subject="S", message="M", is_read=True)

        response = admin_client.get(self.url)
        msgs = response.data["messages"]
        assert msgs["unread"] >= 1
        assert msgs["total"] >= 2


@pytest.mark.django_db
class TestUserSerializerIsStaff:
    """is_staff jest teraz zwracane przez /api/auth/me/ i /api/auth/register/."""

    def test_me_returns_is_staff_false_for_regular_user(self, user_client):
        response = user_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert "is_staff" in response.data
        assert response.data["is_staff"] is False

    def test_me_returns_is_staff_true_for_admin(self, admin_client):
        response = admin_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.data["is_staff"] is True

    def test_register_returns_is_staff_false(self, api_client):
        data = {
            "username": "brandnew",
            "email": "brandnew@test.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == 201
        assert "is_staff" in response.data
        assert response.data["is_staff"] is False


@pytest.mark.django_db
class TestMePatchOptionalFields:
    url = "/api/auth/me/"

    def test_patch_first_name(self, user_client):
        response = user_client.patch(self.url, {"first_name": "Jan"})
        assert response.status_code == 200
        assert response.data["first_name"] == "Jan"

    def test_patch_last_name(self, user_client):
        response = user_client.patch(self.url, {"last_name": "Kowalski"})
        assert response.status_code == 200
        assert response.data["last_name"] == "Kowalski"

    def test_patch_company(self, user_client):
        response = user_client.patch(self.url, {"company": "Acme Sp. z o.o."})
        assert response.status_code == 200
        assert response.data["company"] == "Acme Sp. z o.o."

    def test_patch_multiple_fields_at_once(self, user_client):
        response = user_client.patch(
            self.url,
            {"first_name": "Anna", "last_name": "Nowak", "phone": "600100200"},
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Anna"
        assert response.data["last_name"] == "Nowak"
        assert response.data["phone"] == "600100200"

    def test_patch_saves_to_db(self, user_client, regular_user):
        user_client.patch(self.url, {"first_name": "Zapis"})
        regular_user.refresh_from_db()
        assert regular_user.first_name == "Zapis"


@pytest.mark.django_db
class TestChangePasswordWeakPassword:
    url = "/api/auth/change-password/"

    def test_change_password_weak_new_password(self, user_client):
        data = {
            "old_password": "user123!",
            "new_password": "abc",
            "new_password2": "abc",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 400

    def test_change_password_numeric_only(self, user_client):
        data = {
            "old_password": "user123!",
            "new_password": "12345678",
            "new_password2": "12345678",
        }
        response = user_client.post(self.url, data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestAdminStatsRevenueFormat:
    url = "/api/admin/stats/"

    def test_revenue_completed_is_string_and_reflects_orders(self, admin_client, db):
        from django.contrib.auth import get_user_model
        from orders.models import Order, OrderItem
        from products.models import Category, Product

        U = get_user_model()
        u = U.objects.create_user(username="rev_user", password="pass123!")
        cat = Category.objects.create(name="RevKat", slug="revkat")
        prod = Product.objects.create(name="RevP", slug="revp", price="250.00", category=cat, is_active=True)
        order = Order.objects.create(user=u, status="completed")
        OrderItem.objects.create(order=order, product=prod, quantity=2, unit_price=prod.price)
        order.recalculate_total()

        response = admin_client.get(self.url)
        revenue = response.data["orders"]["revenue_completed"]
        assert isinstance(revenue, str)
        assert float(revenue) >= 500.0
