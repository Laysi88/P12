import pytest
from controller.contrat_controller import ContratController
from model.client import Client
from model.user import User


@pytest.fixture
def contrat_controller(sample_commercial, mock_session, monkeypatch):
    """Fixture qui retourne une instance de ContratController avec une session de test."""

    monkeypatch.setattr("controller.contrat_controller.DBSession", lambda: mock_session)
    controller = ContratController(sample_commercial)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: print(msg))
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: print(msg))
    return controller


def test_create_contrat_success(contrat_controller, sample_client, monkeypatch):
    """Test que create_contrat() crée un contrat avec succès."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: True)

    monkeypatch.setattr(
        contrat_controller.view,
        "input_contrat_info",
        lambda clients: (sample_client.id, 10000, 5000),
    )

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))
    new_contrat = contrat_controller.create_contrat()

    assert new_contrat is not None, "Le contrat doit être créé."
    assert new_contrat.client_id == sample_client.id
    assert new_contrat.total_amount == 10000
    assert new_contrat.remaining_amount == 5000
    assert new_contrat.status is False, "Le contrat doit être non signé par défaut."
    assert new_contrat.date_created is not None, "La date de création doit être définie."

    assert info_message, "Un message de confirmation doit être affiché."
    assert f"✅ Contrat créé avec succès pour le client {sample_client.name} !" in info_message[0]


def test_create_contrat_as_gestionnaire(contrat_controller, sample_client, sample_user, monkeypatch):
    """Test qu'un gestionnaire peut créer un contrat pour n'importe quel client."""

    # 🔹 Modifier le contrôleur pour qu'il utilise un gestionnaire
    contrat_controller.user = sample_user  # On force le rôle à "gestionnaire"

    # 🔹 Simuler l'entrée utilisateur
    monkeypatch.setattr(
        contrat_controller.view,
        "input_contrat_info",
        lambda clients: (sample_client.id, 15000, 7500),  # ✅ Accepte `clients`
    )

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    # 🎯 Exécution
    new_contrat = contrat_controller.create_contrat()

    # ✅ Vérifications
    assert new_contrat is not None, "Le contrat doit être créé par le gestionnaire."
    assert new_contrat.client_id == sample_client.id
    assert new_contrat.total_amount == 15000
    assert new_contrat.remaining_amount == 7500
    assert new_contrat.status is False, "Le contrat doit être non signé par défaut."
    assert info_message, "Un message de confirmation doit être affiché."
    assert f"✅ Contrat créé avec succès pour le client {sample_client.name} !" in info_message[0]


def test_create_contrat_no_client_available(contrat_controller, monkeypatch):
    """Test que create_contrat() refuse de créer un contrat si le client n'existe pas."""

    monkeypatch.setattr(contrat_controller.view, "input_contrat_info", lambda: (999, 10000, 5000))

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.create_contrat()

    assert result is None, "Le contrat ne doit pas être créé."
    assert "⚠️ Aucun client disponible." in error_message[0], "Le message 'Aucun client disponible' doit être affiché."


def test_create_contrat_client_not_found(contrat_controller, mock_session, sample_client, monkeypatch):
    """Test que create_contrat() affiche 'Client inexistant' si le client n'existe pas mais qu'il y a d'autres clients disponibles."""

    another_client = Client(
        name="Client X",
        email="clientX@test.com",
        phone="0101010101",
        company="TestCorp",
        commercial_id=contrat_controller.user.id,
    )
    mock_session.add(another_client)
    mock_session.commit()

    monkeypatch.setattr(contrat_controller.view, "input_contrat_info", lambda clients: (999, 10000, 5000))

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))
    result = contrat_controller.create_contrat()
    assert result is None, "Le contrat ne doit pas être créé."
    assert "⚠️ Client inexistant." in error_message[0], "Le message 'Client inexistant' doit être affiché."


def test_create_contrat_permission_denied(contrat_controller, monkeypatch):
    """Test que create_contrat() retourne None si la permission est refusée."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))
    result = contrat_controller.create_contrat()

    assert result is None, "Le contrat ne doit pas être créé si la permission est refusée."
    assert "❌ Accès refusé" in error_message[0]


def test_create_contrat_for_other_commercial_client(
    contrat_controller, mock_session, sample_client, sample_commercial, monkeypatch
):
    """Test qu'un commercial ne peut pas créer un contrat pour un client qui ne lui appartient pas."""

    autre_commercial = User(
        name="Autre Commercial", email="other@company.com", password="pass", role_id=sample_commercial.role_id
    )
    mock_session.add(autre_commercial)
    mock_session.commit()
    mock_session.refresh(autre_commercial)

    contrat_controller.user = autre_commercial

    client_autre_commercial = Client(
        name="Client de Autre Commercial",
        email="client@autre.com",
        phone="0102020303",
        company="Autre Corp",
        commercial_id=autre_commercial.id,
    )
    mock_session.add(client_autre_commercial)
    mock_session.commit()

    monkeypatch.setattr(
        contrat_controller.view,
        "input_contrat_info",
        lambda clients: (
            sample_client.id,
            12000,
            6000,
        ),
    )

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.create_contrat()

    assert result is None, "Le contrat ne doit pas être créé."
    assert "⚠️ Vous ne pouvez créer un contrat que pour vos propres clients." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_update_contrat_not_authorized_for_other_commercial(
    contrat_controller, mock_session, sample_contrat, sample_commercial, monkeypatch
):
    """Test qu'un commercial ne peut pas modifier un contrat s'il n'est pas affilié au client."""

    autre_commercial = User(
        name="Autre Commercial", email="other@company.com", password="pass", role_id=sample_commercial.role_id
    )
    mock_session.add(autre_commercial)
    mock_session.commit()
    mock_session.refresh(autre_commercial)

    contrat_controller.user = autre_commercial

    monkeypatch.setattr(
        contrat_controller.view,
        "input_update_contrat_info",
        lambda contrat: (12000, 6000, True),
    )

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.update_contrat(sample_contrat.id)

    assert result is None, "Le contrat ne doit pas être mis à jour."
    assert "⚠️ Vous ne pouvez modifier que les contrats de vos propres clients." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_update_contrat_as_gestionnaire(contrat_controller, mock_session, sample_contrat, sample_user, monkeypatch):
    """Test qu'un gestionnaire peut modifier un contrat, peu importe le client."""

    contrat_controller.user = sample_user

    monkeypatch.setattr(
        contrat_controller.view,
        "input_update_contrat_info",
        lambda contrat: (15000, 7500, True),
    )

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    updated_contrat = contrat_controller.update_contrat(sample_contrat.id)

    assert updated_contrat is not None, "Le contrat doit être mis à jour par le gestionnaire."
    assert updated_contrat.total_amount == 15000, "Le montant total doit être mis à jour."
    assert updated_contrat.remaining_amount == 7500, "Le montant restant doit être mis à jour."
    assert updated_contrat.status is True, "Le contrat doit être signé."
    assert f"✅ Contrat {sample_contrat.id} mis à jour avec succès !" in info_message[0]


def test_update_contrat_permission_denied(contrat_controller, sample_contrat, monkeypatch):
    """Test que update_contrat() retourne None si l'utilisateur n'a pas la permission de modifier le contrat."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.update_contrat(sample_contrat.id)

    assert result is None, "Le contrat ne doit pas être modifié."
    assert "❌ Accès refusé : Vous ne pouvez pas modifier ce contrat." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_update_contrat_not_found(contrat_controller, monkeypatch):
    """Test que update_contrat() affiche une erreur si le contrat n'existe pas."""

    fake_contrat_id = 999

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.update_contrat(fake_contrat_id)

    assert result is None, "La mise à jour ne doit pas avoir lieu."
    assert "⚠️ Contrat inexistant." in error_message[0], "Le message d'erreur doit être affiché."
