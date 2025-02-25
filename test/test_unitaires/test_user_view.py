import pytest
from view.user_view import UserView
from model.user import User
from model.client import Client
from model.event import Event
import datetime


@pytest.fixture
def user_view():
    """Fixture qui retourne une instance de UserView."""
    return UserView()


def test_input_infos_user(user_view, monkeypatch):
    inputs = iter(["John", "john@doe.com", "securepass"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name, email, password = user_view.input_infos_user()
    assert name == "John", "Le nom saisi doit être retourné."
    assert email == "john@doe.com", "L'email saisi doit être retourné."
    assert password == "securepass", "Le mot de passe saisi doit être retourné."


def test_choose_role(user_view, monkeypatch):
    inputs = iter(["commercial"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    role = user_view.choose_role()
    assert role == "commercial", "Le rôle choisi doit être retourné."


def test_display_users(user_view, capsys, role_gestion):
    """Test que display_users() affiche correctement la liste des utilisateurs."""

    user1 = User(name="John Doe", email="john@doe.com", password="securepass", role_id=role_gestion.id)
    user1.id = 1
    user1.role = role_gestion

    user2 = User(name="Jane Doe", email="jane@doe.com", password="securepass", role_id=None)
    user2.id = 2

    users = [user1, user2]

    user_view.display_users(users)

    captured = capsys.readouterr()

    assert "📜 Liste des utilisateurs :" in captured.out
    assert f"- {user1.id}: {user1.name} ({user1.email}) - Rôle: {role_gestion.name}" in captured.out
    assert f"- {user2.id}: {user2.name} ({user2.email}) - Rôle: Aucun rôle" in captured.out


def test_display_user_details(user_view, capsys, role_gestion, mock_session):
    """Test que display_user_details() affiche correctement les détails d'un utilisateur."""

    user = User(name="John Doe", email="john@doe.com", password="securepass", role_id=role_gestion.id)
    user.id = 1
    user.role = role_gestion
    client1 = Client(name="Client A", email="clientA@example.com", phone="123456789", company="Company A")
    client2 = Client(name="Client B", email="clientB@example.com", phone="987654321", company="Company B")
    user.clients = [client1, client2]
    event1 = Event(
        name="Événement 1",
        contrat_id=2,
        start_date=datetime.datetime(2025, 12, 13, 0, 0, 0),
        end_date=datetime.datetime(2025, 12, 14, 0, 0, 0),
        support_id=None,
        location="Paris",
        attendees=10,
        notes="Note A",
    )
    event2 = Event(
        name="Événement 2",
        contrat_id=3,
        start_date=datetime.datetime(2022, 6, 13, 0, 0, 0),
        end_date=datetime.datetime(2022, 6, 14, 0, 0, 0),
        support_id=None,
        location="Lyon",
        attendees=20,
        notes="Note B",
    )
    user.events = [event1, event2]
    mock_session.add(user)
    mock_session.add(client1)
    mock_session.add(client2)
    mock_session.add(event1)
    mock_session.add(event2)
    mock_session.commit()
    user_view.display_user_details(user)
    captured = capsys.readouterr()
    assert "👤 Détails de l'utilisateur:" in captured.out
    assert f"🔹 ID : {user.id}" in captured.out
    assert f"🔹 Nom : {user.name}" in captured.out
    assert f"🔹 Email : {user.email}" in captured.out
    assert f"🔹 Rôle : {role_gestion.name}" in captured.out
    assert "🔹 Clients gérés : ['Client A', 'Client B']" in captured.out
    assert "🔹 Événements suivis : ['Événement 1', 'Événement 2']" in captured.out
