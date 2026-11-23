import pytest

from app import create_app
from app.extensions import db
from config import TestConfig


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _register_and_login(client, username):
    client.post("/api/auth/register", json={"username": username, "password": "secret123"})
    res = client.post("/api/auth/login", json={"username": username, "password": "secret123"})
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


@pytest.fixture()
def auth_headers(client):
    return _register_and_login(client, "mahek")


@pytest.fixture()
def other_headers(client):
    return _register_and_login(client, "someone_else")
