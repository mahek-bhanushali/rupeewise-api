def test_register_success(client):
    res = client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    assert res.status_code == 201


def test_register_duplicate_username(client):
    payload = {"username": "alice", "password": "secret123"}
    client.post("/api/auth/register", json=payload)
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={"username": "alice", "password": "123"})
    assert res.status_code == 400


def test_login_returns_token(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    res = client.post("/api/auth/login", json={"username": "alice", "password": "secret123"})
    assert res.status_code == 200
    assert "token" in res.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    res = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert res.status_code == 401


def test_expenses_require_token(client):
    assert client.get("/api/expenses").status_code == 401
