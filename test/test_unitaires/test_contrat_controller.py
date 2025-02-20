import pytest
from controller.contrat_controller import ContratController


@pytest.fixture
def contrat_controller(sample_commercial, mock_session, monkeypatch):
    """Fixture qui retourne une instance de ContratController avec une session de test."""

    monkeypatch.setattr("controller.contrat_controller.DBSession", lambda: mock_session)
    controller = ContratController(sample_commercial)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: print(msg))
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: print(msg))
    return controller


def test_create_contrat_success(contrat_controller, mock_session, sample_client, monkeypatch):
    """Test que create_contrat() crée un contrat avec succès."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: True)

    monkeypatch.setattr(
        contrat_controller.view,
        "input_contrat_info",
        lambda clients: (sample_client.id, 10000, 5000),  # ✅ Accepte `clients`
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


def test_create_contrat_client_not_found(contrat_controller, monkeypatch):
    """Test que create_contrat() refuse de créer un contrat si le client n'existe pas."""

    monkeypatch.setattr(contrat_controller.view, "input_contrat_info", lambda: (999, 10000, 5000))

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = contrat_controller.create_contrat()

    assert result is None, "Le contrat ne doit pas être créé."
    assert "❌ Accès refusé" in error_message[0], "Le message d'accès refusé doit être affiché."


def test_create_contrat_permission_denied(contrat_controller, monkeypatch):
    """Test que create_contrat() retourne None si la permission est refusée."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))
    result = contrat_controller.create_contrat()

    assert result is None, "Le contrat ne doit pas être créé si la permission est refusée."
    assert "❌ Accès refusé" in error_message[0]
