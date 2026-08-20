import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VIEWER_HEADERS = {
    "Authorization": "Bearer phase1-viewer"
}

ADMIN_HEADERS = {
    "Authorization": "Bearer phase1-admin"
}


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_customer_requires_authentication():
    response = client.get("/customers/101")

    assert response.status_code == 401


def test_get_customer():
    response = client.get(
        "/customers/101",
        headers=VIEWER_HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 101
    assert data["name"] == "Customer 101"


def test_customer_not_found():
    response = client.get(
        "/customers/9999999",
        headers=VIEWER_HEADERS
    )

    assert response.status_code == 404


def test_pagination():
    response = client.get(
        "/customers?page=1&limit=20",
        headers=VIEWER_HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["data"]) == 20
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 20
    assert data["pagination"]["total"] == 1_000_000
    assert data["pagination"]["has_next"] is True


def test_pagination_limit_validation():
    response = client.get(
        "/customers?page=1&limit=101",
        headers=VIEWER_HEADERS
    )

    assert response.status_code == 422


def test_viewer_cannot_delete():
    response = client.delete(
        "/customers/101",
        headers=VIEWER_HEADERS
    )

    assert response.status_code == 403


def test_admin_can_delete():
    response = client.delete(
        "/customers/101",
        headers=ADMIN_HEADERS
    )

    assert response.status_code == 204