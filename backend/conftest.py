import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient

User = get_user_model()

# Uruchamia zadania Celery synchronicznie w testach (bez Redis)
pytest_plugins = []


@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123!"
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="user", email="user@test.com", password="user123!"
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_login(admin_user)
    return api_client


@pytest.fixture
def user_client(api_client, regular_user):
    api_client.force_login(regular_user)
    return api_client
