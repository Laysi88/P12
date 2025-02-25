import pytest
from controller.event_controller import EventController
from model.contrat import Contrat
from datetime import datetime


@pytest.fixture
def event_controller(sample_commercial, monkeypatch, mock_session):
    """Fixture qui retourne une instance de EventController avec une session de test."""

    monkeypatch.setattr("controller.event_controller.DBSession", lambda: mock_session)
    controller = EventController(sample_commercial)
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
