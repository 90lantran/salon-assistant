from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.db import engine


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_tables_exist() -> None:
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) >= {
        "appointments",
        "business_hours",
        "customers",
        "feedback",
        "services",
    }
