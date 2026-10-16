"""Simple tests. Success path uses an in-memory MongoDB (mongomock) so no Atlas account is needed;
the error path checks that a failing database shows the error on the same page without redirect.

Run:  pip install mongomock pytest   &&   pytest -v
"""
import mongomock
import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    app_module.app.config["TESTING"] = True
    fake = mongomock.MongoClient()
    monkeypatch.setattr(app_module, "get_collection", lambda: fake["flask_assignment"]["submissions"])
    c = app_module.app.test_client()
    c.fake = fake
    return c


def test_api_returns_json_list(client):
    r = client.get("/api")
    assert r.status_code == 200
    assert r.is_json and isinstance(r.get_json(), list) and len(r.get_json()) == 3


def test_form_page_loads(client):
    assert client.get("/").status_code == 200


def test_submit_success_redirects_and_saves(client):
    r = client.post("/", data={"name": "Harsh", "email": "h@example.com", "message": "Hi"})
    assert r.status_code == 302 and r.headers["Location"].endswith("/success")
    assert client.fake["flask_assignment"]["submissions"].count_documents({}) == 1
    page = client.get("/success")
    assert b"Data submitted successfully" in page.data


def test_validation_error_stays_on_same_page(client):
    r = client.post("/", data={"name": "", "email": "bad", "message": ""})
    assert r.status_code == 400 and b"All fields are required." in r.data


def test_database_error_stays_on_same_page(monkeypatch):
    def boom():
        raise RuntimeError("cannot connect to MongoDB")
    monkeypatch.setattr(app_module, "get_collection", boom)
    c = app_module.app.test_client()
    r = c.post("/", data={"name": "A", "email": "a@b.co", "message": "m"})
    assert r.status_code == 500 and b"Database error" in r.data and b"cannot connect" in r.data
