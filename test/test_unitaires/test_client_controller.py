import pytest
from controller.client_controller import ClientController
from model.client import Client


@pytest.fixture
def client_controller(sample_commercial, mock_session, monkeypatch):
    """Fixture qui retourne un ClientController avec un utilisateur connecté."""

    monkeypatch.setattr("controller.client_controller.DBSession", lambda: mock_session)
    controller = ClientController(sample_commercial)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: None)
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: None)
    monkeypatch.setattr(controller.view, "display_clients", lambda clients: None)
    monkeypatch.setattr(controller.view, "display_client_details", lambda client: None)
    monkeypatch.setattr(
        controller.view, "input_client_info", lambda: ("Client X", "client@example.com", "0612345678", "Entreprise X")
    )

    return controller


def test_create_client(client_controller, mock_session):
    """Test que create_client() crée un client et l'attribue au commercial."""

    initial_count = mock_session.query(Client).count()
    new_client = client_controller.create_client()
    assert new_client is not None, "Le client devrait être créé."
    assert new_client.name == "Client X"
    assert new_client.email == "client@example.com"
    assert new_client.phone == "0612345678"
    assert new_client.company == "Entreprise X"
    assert new_client.commercial_id == client_controller.user.id, (
        "Le client doit être attribué au commercial créateur."
    )
    assert mock_session.query(Client).count() == initial_count + 1, "Le nombre de clients doit augmenter."


def test_create_client_existing_email(client_controller, mock_session):
    """Test que create_client() ne crée pas de client si l'email existe déjà."""

    existing_client = Client(
        name="Client X",
        email="client@example.com",
        phone="0612345678",
        company="Entreprise X",
        commercial_id=client_controller.user.id,
    )
    mock_session.add(existing_client)
    mock_session.commit()
    new_client = client_controller.create_client()
    assert new_client is None, "Le client ne doit pas être créé si l'email existe déjà."


def test_create_client_permission_denied(client_controller, monkeypatch):
    """Test que create_client() retourne None si la permission est refusée."""

    monkeypatch.setattr(client_controller, "check_permission", lambda action: False)
    new_client = client_controller.create_client()
    assert new_client is None, "Le client ne devrait pas être créé."


def test_list_all_clients_as_commercial(client_controller, mock_session):
    """Test qu'un commercial peut voir tous les clients."""
    # 🔹 Création de clients fictifs
    client1 = Client(name="Client A", email="clientA@business.com", phone="0101010101", company="Company A")
    client2 = Client(name="Client B", email="clientB@business.com", phone="0202020202", company="Company B")

    mock_session.add_all([client1, client2])
    mock_session.commit()

    clients = client_controller.list_all_client()

    assert clients is not None, "La fonction ne doit pas retourner None."
    assert len(clients) == 2, "Tous les clients devraient être listés."


def test_list_all_clients_as_permission_denied(client_controller, monkeypatch):
    """Test que list_all_client() retourne None si la permission est refusée."""

    monkeypatch.setattr(client_controller, "check_permission", lambda action: False)
    clients = client_controller.list_all_client()

    assert clients is None, "La liste des clients ne devrait pas être affichée."


def test_list_personnal_clients(client_controller, mock_session, sample_commercial):
    """Test qu'un commercial peut voir ses clients personnels."""
    # 🔹 Création de clients fictifs
    client1 = Client(
        name="Client A",
        email="clientA@business.com",
        phone="0101010101",
        company="Company A",
        commercial_id=sample_commercial.id,
    )
    client2 = Client(
        name="Client B", email="clientB@business.com", phone="0202020202", company="Company B", commercial_id=None
    )

    mock_session.add_all([client1, client2])
    mock_session.commit()

    clients = client_controller.list_personnal_client()

    assert clients is not None, "La fonction ne doit pas retourner None."
    assert len(clients) == 1, "Seuls les clients personnels doivent être listés."


def test_list_personnal_clients_as_permission_denied(client_controller, monkeypatch):
    """Test que list_all_client() retourne None si la permission est refusée."""

    monkeypatch.setattr(client_controller, "check_permission", lambda action: False)
    clients = client_controller.list_personnal_client()

    assert clients is None, "La liste des clients ne devrait pas être affichée."
