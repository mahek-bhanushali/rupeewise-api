def _add(client, headers, **overrides):
    payload = {"title": "Lunch", "amount": 150, "category": "Food", "date": "2026-11-01"}
    payload.update(overrides)
    return client.post("/api/expenses", json=payload, headers=headers)


def test_create_expense(client, auth_headers):
    res = _add(client, auth_headers)
    assert res.status_code == 201
    body = res.get_json()
    assert body["category"] == "food"  # normalised to lowercase
    assert body["amount"] == 150


def test_create_expense_invalid_amount(client, auth_headers):
    assert _add(client, auth_headers, amount=-5).status_code == 400
    assert _add(client, auth_headers, amount="abc").status_code == 400


def test_create_expense_invalid_date(client, auth_headers):
    assert _add(client, auth_headers, date="01-11-2026").status_code == 400


def test_list_and_filter_by_category(client, auth_headers):
    _add(client, auth_headers, category="food")
    _add(client, auth_headers, title="Bus", amount=30, category="travel")
    res = client.get("/api/expenses?category=travel", headers=auth_headers)
    items = res.get_json()["items"]
    assert len(items) == 1 and items[0]["title"] == "Bus"


def test_filter_by_date_range(client, auth_headers):
    _add(client, auth_headers, date="2026-10-01")
    _add(client, auth_headers, date="2026-11-15")
    res = client.get("/api/expenses?start=2026-11-01&end=2026-11-30", headers=auth_headers)
    assert res.get_json()["total"] == 1


def test_update_expense(client, auth_headers):
    expense_id = _add(client, auth_headers).get_json()["id"]
    res = client.put(f"/api/expenses/{expense_id}", json={"amount": 200}, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["amount"] == 200


def test_delete_expense(client, auth_headers):
    expense_id = _add(client, auth_headers).get_json()["id"]
    assert client.delete(f"/api/expenses/{expense_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/expenses/{expense_id}", headers=auth_headers).status_code == 404


def test_cannot_access_other_users_expense(client, auth_headers, other_headers):
    expense_id = _add(client, auth_headers).get_json()["id"]
    res = client.get(f"/api/expenses/{expense_id}", headers=other_headers)
    assert res.status_code == 404


def test_summary(client, auth_headers):
    _add(client, auth_headers, amount=100, category="food")
    _add(client, auth_headers, amount=50, category="food")
    _add(client, auth_headers, amount=30, category="travel")
    body = client.get("/api/expenses/summary", headers=auth_headers).get_json()
    assert body["total"] == 180
    assert body["count"] == 3
