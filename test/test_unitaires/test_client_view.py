import pytest
from view.client_view import ClientView
from model.client import Client
from model.user import User


@pytest.fixture
def client_view():
    """Fixture qui retourne une instance de ClientView."""
    return ClientView()


def test_input_client_info(client_view, monkeypatch):
    """Test que input_client_info() récupère correctement les informations du client."""

    inputs = iter(["Client Test", "client@test.com", "0601020304", "TestCorp"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name, email, phone, company = client_view.input_client_info()
    assert name == "Client Test", "Le nom du client doit être correctement récupéré."
    assert email == "client@test.com", "L'email du client doit être correctement récupéré."
    assert phone == "0601020304", "Le téléphone du client doit être correctement récupéré."
    assert company == "TestCorp", "L'entreprise du client doit être correctement récupérée."


def test_display_info_message(client_view, capsys):
    """Test de display_info_message()."""
    client_view.display_info_message("Ceci est une info.")
    captured = capsys.readouterr()
    assert "ℹ️ Ceci est une info." in captured.out


def test_display_error_message(client_view, capsys):
    """Test de display_error_message()."""
    client_view.display_error_message("Ceci est une erreur.")
    captured = capsys.readouterr()
    assert "❌ Ceci est une erreur." in captured.out


def test_display_clients_empty(client_view, capsys):
    """Test de display_clients() avec une liste vide."""
    client_view.display_clients([])
    captured = capsys.readouterr()
    assert "\n📜 Aucun client à afficher." in captured.out


def test_display_client_details(client_view, capsys):
    """Test que display_client_details() affiche correctement les détails d'un client."""

    commercial = User(name="John Commercial", email="john@company.com", password="securepass", role_id=2)
    client = Client(id=1, name="Client X", email="client@business.com", phone="123456789", company="Business Corp")
    client.commercial = commercial
    client_view.display_client_details(client)
    captured = capsys.readouterr()
    assert "\n👤 Détails du client :" in captured.out
    assert "🔹 ID : 1" in captured.out
    assert "🔹 Nom : Client X" in captured.out
    assert "🔹 Email : client@business.com" in captured.out
    assert "🔹 Téléphone : 123456789" in captured.out
    assert "🔹 Entreprise : Business Corp" in captured.out
    assert "🔹 Commercial : John Commercial" in captured.out


def test_display_client_details_no_commercial(client_view, capsys):
    """Test que display_client_details() affiche 'Non attribué' si aucun commercial n'est assigné."""

    client = Client(id=2, name="Client Y", email="clientY@business.com", phone="987654321", company="Tech Corp")
    client.commercial = None
    client_view.display_client_details(client)
    captured = capsys.readouterr()
    assert "🔹 Commercial : Non attribué" in captured.out
