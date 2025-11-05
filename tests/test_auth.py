import pytest
from flask import Flask
from flask.testing import FlaskClient

from flaskr import create_app, db

@pytest.fixture
def app():
    database = "file:mem1?mode=memory&cache=shared"
    app = create_app(database)
    db.init_db(database)
    return app

@pytest.fixture
def client(app: Flask):
    return app.test_client()

def test_register_get(client: FlaskClient):
    response = client.get("/auth/register")

    assert response.status_code == 200

def test_register_post(app: Flask, client: FlaskClient):
    response = client.post("/auth/register", data={"username": "a", "password": "a"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert (
            db.get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )

def test_register_no_username(client):
    response = client.post("/auth/register", data={"username": "", "password": ""})
    assert b"Username is required." in response.data

def test_register_no_password(client):
    response = client.post("/auth/register", data={"username": "test", "password": ""})
    assert b"Password is required." in response.data

# def test_register_existing_user(client):
#     conn = db.get_db()
#     conn.execute(
#         "INSERT INTO user (username, password) VALUES "
#         "('test', 'scrypt:32768:8:1$B6EWUB7sblZHpKwE$74951791e0ebcdcf91999e0e4c3e7768fcb87f994c35de0d80e99d83ec36e9f542b76c4d486c57ced5cea72fd76c3f5a64b0a2c31a89a02e3a86a52a6f52fb1c')"
#     )
#     conn.commit()
#     response = client.post("/auth/register", data={"username": "test", "password": "b"})
#     assert b"already registered" in response.data

def test_login_get(client: FlaskClient):
    response = client.get("/auth/login")

    assert response.status_code == 200

def test_login(client):
    conn = db.get_db()
    conn.execute(
        "INSERT INTO user (username, password) VALUES "
        "('test', 'scrypt:32768:8:1$B6EWUB7sblZHpKwE$74951791e0ebcdcf91999e0e4c3e7768fcb87f994c35de0d80e99d83ec36e9f542b76c4d486c57ced5cea72fd76c3f5a64b0a2c31a89a02e3a86a52a6f52fb1c')"
    )
    conn.commit()
    assert client.get("/auth/login").status_code == 200
    response = client.post("/auth/login", data={"username": "test", "password": "test"})
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"

@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", "Incorrect username."),
        ("test", "a", "Incorrect password."),
    ),
)
def test_login_validate_input(client, username, password, message):
    conn = db.get_db()
    conn.execute(
        "INSERT INTO user (username, password) VALUES "
        "('test', 'scrypt:32768:8:1$B6EWUB7sblZHpKwE$74951791e0ebcdcf91999e0e4c3e7768fcb87f994c35de0d80e99d83ec36e9f542b76c4d486c57ced5cea72fd76c3f5a64b0a2c31a89a02e3a86a52a6f52fb1c')"
    )
    conn.commit()
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    assert message in response.text