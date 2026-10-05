import pytest
from django.db import connection
from django.urls import reverse


@pytest.mark.django_db
def test_health_reports_ok(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_postgis_extension_is_available():
    with connection.cursor() as cursor:
        cursor.execute("SELECT postgis_version()")
        (version,) = cursor.fetchone()

    assert version
