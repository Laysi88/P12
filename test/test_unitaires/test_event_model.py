import pytest
from model.event import Event
from datetime import datetime
import re


def test_validate_dates():
    """Test que la validation des dates empêche une date de fin incorrecte."""

    event = Event(
        name="Conférence Tech",
        contrat_id=1,
        start_date=datetime(2025, 6, 1, 10, 0),
        end_date=datetime(2025, 6, 2, 18, 0),
        location="Paris",
        attendees=100,
    )
    assert event.end_date > event.start_date

    with pytest.raises(ValueError, match="La date de fin doit être postérieure à la date de début."):
        Event(
            name="Conférence Tech",
            contrat_id=1,
            start_date=datetime(2025, 6, 2, 18, 0),
            end_date=datetime(2025, 6, 1, 10, 0),
            location="Paris",
            attendees=100,
        )


def test_validate_attendees():
    """Test que la validation empêche un nombre négatif de participants."""

    event = Event(
        name="Salon de l'IA",
        contrat_id=2,
        start_date=datetime(2025, 7, 10, 9, 0),
        end_date=datetime(2025, 7, 12, 17, 0),
        location="Lyon",
        attendees=50,
    )
    assert event.attendees == 50

    with pytest.raises(ValueError, match="Le nombre de participants ne peut pas être négatif."):
        Event(
            name="Salon de l'IA",
            contrat_id=2,
            start_date=datetime(2025, 7, 10, 9, 0),
            end_date=datetime(2025, 7, 12, 17, 0),
            location="Lyon",
            attendees=-5,
        )


def test_repr_event():
    """Test de la représentation textuelle d'un événement."""
    event = Event(
        name="Conférence Tech",
        contrat_id=1,
        start_date=datetime(2025, 6, 1, 10, 0),
        end_date=datetime(2025, 6, 2, 18, 0),
        location="Paris",
        attendees=100,
    )
    assert isinstance(repr(event), str), "Le __repr__ doit retourner une chaîne de caractères."
    pattern = (
        r"<Event\(id=None, name=Conférence Tech, start_date=2025-06-01 10:00:00, "
        r"end_date=2025-06-02 18:00:00, location=Paris, attendees=100\)>"
    )
    assert re.match(pattern, repr(event)), f"La représentation textuelle est incorrecte : {repr(event)}"
