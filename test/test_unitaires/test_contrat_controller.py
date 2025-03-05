import pytest
from controller.contrat_controller import ContratController
from model.client import Client
from model.user import User
from model.contrat import Contrat


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


def test_create_contrat_cancelled(contrat_controller, sample_client, monkeypatch):
    """Test que la création de contrat est annulée proprement si l'utilisateur appuie sur Entrée."""

    contrat_controller.session.add(sample_client)
    contrat_controller.session.commit()

    monkeypatch.setattr("builtins.input", lambda _: "")

    result = contrat_controller.create_contrat()
    assert result is None, "La création du contrat doit être annulée et ne rien retourner."


def test_create_contrat_as_gestionnaire(contrat_controller, sample_client, sample_user, monkeypatch):
    """Test qu'un gestionnaire peut créer un contrat pour n'importe quel client."""

    contrat_controller.user = sample_user
    monkeypatch.setattr(
        contrat_controller.view,
        "input_contrat_info",
        lambda clients: (sample_client.id, 15000, 7500),
    )
    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))
    new_contrat = contrat_controller.create_contrat()

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


def test_create_contrat_client_not_found(contrat_controller, mock_session, monkeypatch):
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


def test_update_contrat_as_gestionnaire(contrat_controller, sample_contrat, sample_user, monkeypatch):
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


def test_display_all_contrats(contrat_controller, mock_session, sample_client, monkeypatch):
    """Test que display_all_contrats affiche tous les contrats si l'utilisateur a la permission."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: action == "read_contrat")

    contrat1 = Contrat(client_id=sample_client.id, total_amount=5000, remaining_amount=1000, status=False)
    contrat2 = Contrat(client_id=sample_client.id, total_amount=10000, remaining_amount=0, status=True)

    mock_session.add_all([contrat1, contrat2])
    mock_session.commit()

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    contrats = contrat_controller.read_contrat()

    assert contrats is not None, "La fonction doit retourner une liste de contrats"
    assert len(contrats) == 2, "Deux contrats doivent être affichés"
    assert not info_message, "Aucun message ne doit être affiché si des contrats existent"


def test_display_all_contrats_no_permission(contrat_controller, monkeypatch):
    """Test que display_all_contrats refuse l'accès sans permission."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    contrats = contrat_controller.read_contrat()

    assert contrats == [], "Sans permission, aucun contrat ne doit être retourné"
    assert "❌ Accès refusé" in error_message[0], "Un message d'erreur doit être affiché"


def test_display_all_contrats_empty(contrat_controller, mock_session, monkeypatch):
    """Test que display_all_contrats affiche un message si aucun contrat n'est trouvé."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda action: action == "read_contrat")

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    contrats = contrat_controller.read_contrat()

    assert contrats == [], "La liste doit être vide si aucun contrat n'est trouvé"
    assert "📭 Aucun contrat trouvé." in info_message[0], "Le message d'absence de contrat doit être affiché"


def test_filter_contrats_non_signes(contrat_controller, mock_session, sample_client, monkeypatch):
    """Test que filter_contrats retourne uniquement les contrats non signés."""

    contrat_1 = Contrat(client_id=sample_client.id, total_amount=5000, remaining_amount=2000, status=False)
    contrat_2 = Contrat(client_id=sample_client.id, total_amount=7000, remaining_amount=0, status=True)

    mock_session.add_all([contrat_1, contrat_2])
    mock_session.commit()

    monkeypatch.setattr(contrat_controller.view, "ask_filter_option", lambda: "non_signes")
    monkeypatch.setattr(contrat_controller, "check_permission", lambda _: True)

    contrats = contrat_controller.filter_contrats()

    assert contrats == [contrat_1], "Seuls les contrats non signés doivent être retournés."


def test_filter_contrats_paiement_en_attente(contrat_controller, mock_session, sample_client, monkeypatch):
    """Test que filter_contrats retourne uniquement les contrats avec paiement en attente."""

    contrat_1 = Contrat(client_id=sample_client.id, total_amount=5000, remaining_amount=2000, status=True)
    contrat_2 = Contrat(client_id=sample_client.id, total_amount=7000, remaining_amount=0, status=True)

    mock_session.add_all([contrat_1, contrat_2])
    mock_session.commit()

    monkeypatch.setattr(contrat_controller.view, "ask_filter_option", lambda: "paiement_en_attente")
    monkeypatch.setattr(contrat_controller, "check_permission", lambda _: True)

    contrats = contrat_controller.filter_contrats()

    assert contrats == [contrat_1], "Seuls les contrats avec un reste à payer doivent être retournés."


def test_filter_contrats_invalid_option(contrat_controller, monkeypatch):
    """Test que filter_contrats affiche une erreur en cas d'option invalide."""

    monkeypatch.setattr(contrat_controller.view, "ask_filter_option", lambda: "invalid_option")
    monkeypatch.setattr(contrat_controller, "check_permission", lambda _: True)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    contrats = contrat_controller.filter_contrats()

    assert contrats == [], "Aucun contrat ne doit être retourné avec une option invalide."
    assert "❌ Option invalide." in error_message, "Un message d'erreur doit être affiché."


def test_filter_permisson(contrat_controller, monkeypatch):
    """Test que filter_contrats affiche une erreur si l'utilisateur n'a pas la permission."""

    monkeypatch.setattr(contrat_controller, "check_permission", lambda _: False)

    error_message = []
    monkeypatch.setattr(contrat_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    contrats = contrat_controller.filter_contrats()

    assert contrats == [], "Aucun contrat ne doit être retourné si la permission est refusée."
    assert "❌ Accès refusé : Vous n'avez pas la permission d'afficher les contrats." in error_message, (
        "Un message d'erreur doit être affiché."
    )


def test_no_contrat_to_display_for_filter(contrat_controller, monkeypatch):
    """Test que filter_contrats affiche un message si aucun contrat n'est à afficher."""

    monkeypatch.setattr(contrat_controller.view, "ask_filter_option", lambda: "non_signes")
    monkeypatch.setattr(contrat_controller, "check_permission", lambda _: True)

    info_message = []
    monkeypatch.setattr(contrat_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    contrats = contrat_controller.filter_contrats()

    assert contrats == [], "Aucun contrat ne doit être retourné."
    assert "📭 Aucun contrat trouvé pour ce filtre." in info_message, "Un message informatif doit être affiché."
