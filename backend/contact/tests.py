import pytest
from contact.models import ContactMessage


@pytest.fixture
def message(db):
    return ContactMessage.objects.create(
        name="Jan Kowalski",
        email="jan@test.com",
        subject="Zapytanie",
        message="Treść wiadomości testowej.",
    )


@pytest.mark.django_db
class TestContactMessageAPI:
    url = "/api/contact/"

    def test_send_message_anonymous(self, api_client):
        data = {
            "name": "Anna Nowak",
            "email": "anna@test.com",
            "subject": "Wycena",
            "message": "Proszę o wycenę strony.",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 201
        assert ContactMessage.objects.filter(email="anna@test.com").exists()

    def test_send_message_missing_fields(self, api_client):
        response = api_client.post(self.url, {"name": "Anna"})
        assert response.status_code == 400

    def test_send_message_invalid_email(self, api_client):
        data = {
            "name": "Anna",
            "email": "nie-email",
            "subject": "Test",
            "message": "Treść.",
        }
        response = api_client.post(self.url, data)
        assert response.status_code == 400

    def test_list_messages_admin(self, admin_client, message):
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_messages_forbidden_for_user(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == 403

    def test_list_messages_forbidden_anonymous(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_retrieve_message_admin(self, admin_client, message):
        response = admin_client.get(f"{self.url}{message.pk}/")
        assert response.status_code == 200
        assert response.data["email"] == "jan@test.com"

    def test_mark_read(self, admin_client, message):
        assert message.is_read is False
        response = admin_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": True})
        assert response.status_code == 200
        message.refresh_from_db()
        assert message.is_read is True

    def test_mark_read_forbidden_for_user(self, user_client, message):
        response = user_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": True})
        assert response.status_code == 403

    def test_delete_message_admin(self, admin_client, message):
        response = admin_client.delete(f"{self.url}{message.pk}/")
        assert response.status_code == 204
        assert not ContactMessage.objects.filter(pk=message.pk).exists()

    def test_delete_message_forbidden_for_user(self, user_client, message):
        response = user_client.delete(f"{self.url}{message.pk}/")
        assert response.status_code == 403

    def test_delete_message_forbidden_anonymous(self, api_client, message):
        response = api_client.delete(f"{self.url}{message.pk}/")
        assert response.status_code == 403

    def test_delete_nonexistent_message(self, admin_client):
        response = admin_client.delete(f"{self.url}99999/")
        assert response.status_code == 404

    def test_mark_unread(self, admin_client, message):
        message.is_read = True
        message.save()
        response = admin_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": False})
        assert response.status_code == 200
        message.refresh_from_db()
        assert message.is_read is False

    def test_mark_read_anonymous(self, api_client, message):
        response = api_client.patch(f"{self.url}{message.pk}/mark-read/", {"is_read": True})
        assert response.status_code == 403

    def test_message_is_unread_by_default(self, api_client):
        data = {
            "name": "Nowy",
            "email": "nowy@test.com",
            "subject": "Nowe zapytanie",
            "message": "Treść nowego zapytania.",
        }
        api_client.post(self.url, data)
        msg = ContactMessage.objects.get(email="nowy@test.com")
        assert msg.is_read is False

    def test_multiple_messages_listed(self, admin_client, message):
        ContactMessage.objects.create(
            name="Druga", email="druga@test.com",
            subject="Drugi temat", message="Druga treść.",
        )
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_retrieve_nonexistent_message(self, admin_client):
        response = admin_client.get(f"{self.url}99999/")
        assert response.status_code == 404
