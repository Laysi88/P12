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


def test_update_client(client_controller, mock_session, sample_commercial, monkeypatch):
    """Test que update_client() met à jour les informations d'un client."""

    client = Client(
        name="Old Name",
        email="old@email.com",
        phone="0101010101",
        company="Old Company",
        commercial_id=sample_commercial.id,
    )
    mock_session.add(client)
    mock_session.commit()
    monkeypatch.setattr(
        client_controller.view, "input_client_info", lambda: ("New Name", "new@email.com", "0202020202", "New Company")
    )
    client_controller.update_client(client.id)
    updated_client = mock_session.query(Client).filter_by(id=client.id).first()
    assert updated_client.name == "New Name"
    assert updated_client.email == "new@email.com"
    assert updated_client.phone == "0202020202"
    assert updated_client.company == "New Company"


def test_update_client_not_found(client_controller, mock_session, capsys):
    """Test que update_client() affiche une erreur si le client n'existe pas."""

    client_id = 999
    client_controller.update_client(client_id)

    captured = capsys.readouterr()
    assert "⚠️ Le client n'existe pas." in captured.out


def test_update_client_email_already_used(client_controller, mock_session, sample_commercial, monkeypatch, capsys):
    """Test que update_client() refuse un email déjà utilisé."""

    client1 = Client(
        name="Client A",
        email="email@used.com",
        phone="0101010101",
        company="Company A",
        commercial_id=sample_commercial.id,
    )
    client2 = Client(
        name="Client B",
        email="old@email.com",
        phone="0202020202",
        company="Company B",
        commercial_id=sample_commercial.id,
    )

    mock_session.add_all([client1, client2])
    mock_session.commit()
    monkeypatch.setattr(
        client_controller.view,
        "input_client_info",
        lambda: ("New Name", "email@used.com", "0303030303", "New Company"),
    )

    client_controller.update_client(client2.id)
    captured = capsys.readouterr()
    assert "⚠️ Email déjà utilisé." in captured.out


def test_update_client_empty_fields(client_controller, mock_session, sample_commercial, monkeypatch):
    """Test que update_client() conserve les valeurs si on ne renseigne pas tous les champs."""

    client = Client(
        name="Old Name",
        email="old@email.com",
        phone="0101010101",
        company="Old Company",
        commercial_id=sample_commercial.id,
    )
    mock_session.add(client)
    mock_session.commit()
    monkeypatch.setattr(client_controller.view, "input_client_info", lambda: ("", "", "", "New Company"))
    client_controller.update_client(client.id)
    updated_client = mock_session.query(Client).filter_by(id=client.id).first()

    assert updated_client.name == "Old Name"
    assert updated_client.email == "old@email.com"
    assert updated_client.phone == "0101010101"
    assert updated_client.company == "New Company"


def test_update_client_permission_denied(client_controller, monkeypatch):
    """Test que update_client() retourne None si la permission est refusée."""

    monkeypatch.setattr(client_controller, "check_permission", lambda action: False)
    return_value = client_controller.update_client(1)
    assert return_value is None, "Le client ne devrait pas être mis à jour."
