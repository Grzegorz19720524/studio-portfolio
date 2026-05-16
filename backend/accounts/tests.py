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
