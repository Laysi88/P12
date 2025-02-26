import pytest
from controller.event_controller import EventController
from model.contrat import Contrat
from datetime import datetime
from model.event import Event


@pytest.fixture
def event_controller(sample_commercial, monkeypatch, mock_session):
    """Fixture qui retourne une instance de EventController avec une session de test."""

    monkeypatch.setattr("controller.event_controller.DBSession", lambda: mock_session)
    controller = EventController(sample_commercial)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: print(msg))
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: print(msg))
    return controller


@pytest.fixture
def event_controller_support(sample_support, monkeypatch, mock_session):
    """Fixture pour un `EventController` avec un utilisateur support."""
    monkeypatch.setattr("controller.event_controller.DBSession", lambda: mock_session)
    controller = EventController(sample_support)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: print(msg))
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: print(msg))
    return controller


@pytest.fixture
def event_controller_gestion(sample_user, monkeypatch, mock_session):
    """Fixture pour un `EventController` avec un utilisateur gestionnaire."""
    monkeypatch.setattr("controller.event_controller.DBSession", lambda: mock_session)
    controller = EventController(sample_user)
    monkeypatch.setattr(controller.view, "display_info_message", lambda msg: print(msg))
    monkeypatch.setattr(controller.view, "display_error_message", lambda msg: print(msg))
    return controller


def test_create_event_success(event_controller, sample_contrat, monkeypatch):
    """Test qu'un commercial peut créer un événement pour un contrat signé."""

    sample_contrat.status = True
    event_controller.session.commit()
    event_controller.session.refresh(sample_contrat)

    monkeypatch.setattr(
        event_controller.view,
        "input_event_info",
        lambda _: (
            sample_contrat.id,
            "Soirée VIP",
            datetime(2025, 6, 10),
            datetime(2025, 6, 11),
            "Paris",
            50,
            None,
            "Cocktail d'affaires",
        ),
    )

    info_message = []
    monkeypatch.setattr(event_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    new_event = event_controller.create_event()

    assert new_event is not None, "L'événement doit être créé."
    assert new_event.name == "Soirée VIP"
    assert new_event.contrat_id == sample_contrat.id
    assert new_event.start_date == datetime(2025, 6, 10)
    assert new_event.end_date == datetime(2025, 6, 11)
    assert new_event.location == "Paris"
    assert new_event.attendees == 50
    assert new_event.notes == "Cocktail d'affaires"
    assert info_message, "Un message de confirmation doit être affiché."
    assert f"✅ Événement 'Soirée VIP' créé avec succès pour le contrat {sample_contrat.id} !" in info_message[0]


def test_create_event_permission_denied(event_controller, monkeypatch):
    """Test qu'un utilisateur sans permission ne peut pas créer un événement."""

    monkeypatch.setattr(event_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(event_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = event_controller.create_event()

    assert result is None, "L'événement ne doit pas être créé si l'accès est refusé."
    assert "❌ Accès refusé : Vous ne pouvez pas créer un événement." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_create_event_no_disponible_contrat(event_controller, monkeypatch, mock_session):
    """Test qu'un événement ne peut pas être créé s'il n'y a aucun contrat signé."""

    mock_session.query(Contrat).delete()
    mock_session.commit()

    error_message = []
    monkeypatch.setattr(event_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = event_controller.create_event()

    assert result is None, "L'événement ne doit pas être créé s'il n'y a aucun contrat signé."
    assert "⚠️ Aucun contrat signé disponible pour créer un événement." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_create_event_contrat_inexistant(event_controller, monkeypatch, mock_session):
    """Test qu'un événement ne peut pas être créé si le contrat est inexistant."""

    contrat_valide = Contrat(
        client_id=1,
        total_amount=10000,
        remaining_amount=5000,
        status=True,
    )
    mock_session.add(contrat_valide)
    mock_session.commit()
    mock_session.refresh(contrat_valide)

    monkeypatch.setattr(
        event_controller.view,
        "input_event_info",
        lambda _: (
            "Conférence Tech",
            999,
            datetime(2025, 9, 10),
            datetime(2025, 9, 12),
            "Marseille",
            100,
            None,
            "Événement important",
        ),
    )

    error_message = []
    monkeypatch.setattr(event_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = event_controller.create_event()

    assert result is None, "L'événement ne doit pas être créé si le contrat est inexistant."
    assert "⚠️ Contrat inexistant." in error_message[0], (
        "Le message d'erreur doit être affiché pour un contrat inexistant."
    )


def test_read_event_success(event_controller, sample_event, monkeypatch):
    """Test qu'un utilisateur peut lire tous les événements."""

    monkeypatch.setattr(event_controller.session.query(Event), "all", lambda: [sample_event])

    result = event_controller.read_event()

    assert result == [sample_event], "Les événements doivent être retournés."
    assert len(result) == 1, "Un seul événement doit être retourné."


def test_read_event_permission_denied(event_controller, monkeypatch):
    """Test qu'un utilisateur sans permission ne peut pas lire les événements."""

    monkeypatch.setattr(event_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(event_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    result = event_controller.read_event()

    assert result == [], "Aucun événement ne doit être retourné si l'accès est refusé."
    assert "❌ Accès refusé : Vous ne pouvez pas lire un événement." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_read_event_no_event(event_controller, monkeypatch):
    """Test qu'un message est affiché s'il n'y a aucun événement."""

    monkeypatch.setattr(event_controller.session.query(Event), "all", lambda: [])

    info_message = []
    monkeypatch.setattr(event_controller.view, "display_info_message", lambda msg: info_message.append(msg))

    result = event_controller.read_event()

    assert result == [], "Aucun événement ne doit être retourné s'il n'y en a pas."
    assert "📭 Aucun événement disponible." in info_message[0], "Le message d'information doit être affiché."


def test_filter_event_as_support(event_controller_support, sample_event, monkeypatch):
    """Test que le support ne voit que les événements qui lui sont attribués."""

    sample_event.support_id = event_controller_support.user.id
    event_controller_support.session.commit()

    monkeypatch.setattr(
        event_controller_support.session.query(Event),
        "filter_by",
        lambda support_id: [sample_event] if support_id == event_controller_support.user.id else [],
    )

    result = event_controller_support.filter_event()

    assert result == [sample_event], "Le support doit voir uniquement ses événements."


def test_filter_event_as_gestion(event_controller_gestion, sample_event, monkeypatch):
    """Test que le gestionnaire ne voit que les événements sans support."""

    sample_event.support_id = None
    event_controller_gestion.session.commit()

    monkeypatch.setattr(
        event_controller_gestion.session.query(Event),
        "filter_by",
        lambda support_id: [sample_event] if support_id is None else [],
    )

    result = event_controller_gestion.filter_event()

    assert result == [sample_event], "Le gestionnaire doit voir uniquement les événements sans support."


def test_filter_event_no_permission(event_controller_support, monkeypatch):
    """Test qu'un utilisateur sans permission ne peut pas filtrer les événements."""

    monkeypatch.setattr(event_controller_support, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(event_controller_support.view, "display_error_message", lambda msg: error_message.append(msg))

    result = event_controller_support.filter_event()

    assert result == [], "L'utilisateur sans permission ne doit voir aucun événement."
    assert "❌ Accès refusé : Vous ne pouvez pas filtrer les événements." in error_message[0]


def test_filter_event_no_event(event_controller_support, monkeypatch):
    """Test qu'un message est affiché s'il n'y a aucun événement à filtrer."""

    monkeypatch.setattr(event_controller_support.session.query(Event), "all", lambda: [])

    info_message = []
    monkeypatch.setattr(event_controller_support.view, "display_info_message", lambda msg: info_message.append(msg))

    result = event_controller_support.filter_event()

    assert result == [], "Aucun événement ne doit être retourné s'il n'y en a pas."
    assert "📭 Aucun événement trouvé pour ce filtre." in info_message[0], (
        "Le message d'information doit être affiché."
    )


def test_update_event_assign_support(event_controller_gestion, sample_event, sample_support, monkeypatch):
    """Test qu'un gestionnaire peut assigner un support à un événement."""

    event_controller_gestion.user.role.name = "gestion"

    monkeypatch.setattr(event_controller_gestion.view, "input_support_assignment", lambda: sample_support.id)

    info_message = []
    monkeypatch.setattr(event_controller_gestion.view, "display_info_message", lambda msg: info_message.append(msg))

    event_controller_gestion.update_event(sample_event.id)

    assert sample_event.support_id == sample_support.id, "Le support doit être attribué à l'événement."
    assert info_message, "Un message de confirmation doit être affiché."
    assert f"✅ Événement {sample_event.id} mis à jour avec succès !" in info_message[0]


def test_update_event_update_note(event_controller_support, sample_event, monkeypatch):
    """Test qu'un support peut mettre à jour les notes d'un événement."""

    event_controller_support.user.role.name = "support"

    new_notes = "Nouvelles notes"
    monkeypatch.setattr(event_controller_support.view, "input_update_notes", lambda: new_notes)

    info_message = []
    monkeypatch.setattr(event_controller_support.view, "display_info_message", lambda msg: info_message.append(msg))

    event_controller_support.update_event(sample_event.id)

    assert sample_event.notes == "Nouvelles notes", "Les notes de l'événement doivent être mises à jour."
    assert info_message, "Un message de confirmation doit être affiché."
    assert f"✅ Événement {sample_event.id} mis à jour avec succès !" in info_message[0]


def test_update_event_permission_denied(event_controller, sample_event, monkeypatch):
    """Test qu'un utilisateur sans permission ne peut pas mettre à jour un événement."""

    monkeypatch.setattr(event_controller, "check_permission", lambda action: False)

    error_message = []
    monkeypatch.setattr(event_controller.view, "display_error_message", lambda msg: error_message.append(msg))

    event_controller.update_event(sample_event.id)

    assert sample_event.support_id is None, "L'événement ne doit pas être mis à jour si l'accès est refusé."
    assert "❌ Accès refusé : Vous ne pouvez pas modifier cet événement." in error_message[0], (
        "Le message d'erreur doit être affiché."
    )


def test_update_event_inexistant(event_controller_gestion, monkeypatch):
    """Test qu'un message est affiché si l'événement n'existe pas."""

    error_message = []
    monkeypatch.setattr(event_controller_gestion.view, "display_error_message", lambda msg: error_message.append(msg))

    event_controller_gestion.update_event(999)

    assert "⚠️ Événement inexistant." in error_message[0], (
        "Le message d'erreur doit être affiché pour un événement inexistant."
    )
