import pytest
from view.event_view import EventView


@pytest.fixture
def event_view():
    """Fixture qui retourne une instance de EventView."""
    return EventView()


def test_display_info_message(event_view, capsys):
    """Test que display_info_message() affiche correctement un message d'information."""

    event_view.display_info_message("Message d'information")
    captured = capsys.readouterr()
    assert " Message d'information" in captured.out


def test_display_error_message(event_view, capsys):
    """Test que display_error_message() affiche correctement un message d'erreur."""

    event_view.display_error_message("Message d'erreur")
    captured = capsys.readouterr()
    assert " Message d'erreur" in captured.out


def test_input_event_info(event_view, monkeypatch):
    """Test que `input_event_info` capture correctement les entrées utilisateur."""

    # 🔹 Simuler les entrées utilisateur
    inputs = iter(
        [
            "Soirée Networking",
            "2025-07-10 18:00",
            "2025-07-10 22:00",
            "Paris",
            "150",
            "",
            "Cocktail et discussions professionnelles",  # Notes
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    name, start_date, end_date, location, attendees, support_id, notes = event_view.input_event_info()

    assert name == "Soirée Networking"
    assert start_date == "2025-07-10 18:00"
    assert end_date == "2025-07-10 22:00"
    assert location == "Paris"
    assert attendees == 150
    assert support_id is None
    assert notes == "Cocktail et discussions professionnelles"
