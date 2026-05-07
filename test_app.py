import pytest

from app import create_app
from models import db


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
        }
    )

    with app.app_context():
        db.create_all()
        yield app.test_client()


def test_registration_success(client):
    response = client.post(
        "/register",
        json={"nome": "Usuário", "email": "usuario@example.com", "senha": "Senha123"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "cadastro realizado"
    assert data["user"]["email"] == "usuario@example.com"
    assert data["user"]["nome"] == "Usuário"


def test_registration_duplicate_email(client):
    client.post(
        "/register",
        json={"nome": "Usuário", "email": "dup@example.com", "senha": "Senha123"},
    )

    response = client.post(
        "/register",
        json={"nome": "Outro", "email": "dup@example.com", "senha": "Senha123"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "email já cadastrado"


def test_login_with_valid_credentials(client):
    client.post(
        "/register",
        json={"nome": "Login", "email": "login@example.com", "senha": "Senha123"},
    )

    response = client.post(
        "/login",
        json={"email": "login@example.com", "senha": "Senha123"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "login realizado"
    assert data["user"]["email"] == "login@example.com"


def test_login_with_invalid_credentials(client):
    client.post(
        "/register",
        json={"nome": "Login", "email": "login-invalid@example.com", "senha": "Senha123"},
    )

    response = client.post(
        "/login",
        json={"email": "login-invalid@example.com", "senha": "SenhaErrada"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "credenciais inválidas"
