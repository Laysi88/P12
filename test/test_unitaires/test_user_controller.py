import pytest
from controller.user_controller import UserController
from model.user import User


@pytest.fixture
def user_controller(sample_user, mock_session, monkeypatch):
    """Crée une instance de UserController en réutilisant sample_user et mock_session."""

    monkeypatch.setattr("controller.user_controller.DBSession", lambda: mock_session)
    controller = UserController(sample_user)
    monkeypatch.setattr(controller.view, "input_infos_user", lambda: ("Alice", "alice@example.com", "securepass"))
    monkeypatch.setattr(controller.view, "choose_role", lambda: "commercial")

    return controller


def test_create_user(user_controller, mock_session, role_commercial):
    """Teste la création d'un utilisateur."""
    initial_count = mock_session.query(User).count()
    new_user = user_controller.create_user()
    assert new_user is not None, "L'utilisateur devrait être créé."
    assert new_user.name == "Alice"
    assert new_user.email == "alice@example.com"
    assert new_user.role_id == role_commercial.id
    assert mock_session.query(User).count() == initial_count + 1, "Le nombre d'utilisateurs doit augmenter."


def test_delete_user(user_controller, mock_session, sample_user):
    """Teste la suppression d'un utilisateur."""
    initial_count = mock_session.query(User).count()
    user_controller.delete_user(sample_user.id)
    assert mock_session.query(User).count() == initial_count - 1, "Le nombre d'utilisateurs doit diminuer."


def test_delete_user_permission_denied(user_controller, mock_session, sample_user, monkeypatch):
    """Test que delete_user() ne supprime pas l'utilisateur si la permission est refusée."""
    monkeypatch.setattr(user_controller, "check_permission", lambda action: False)
    initial_count = mock_session.query(User).count()
    user_controller.delete_user(sample_user.id)
    assert mock_session.query(User).count() == initial_count, "L'utilisateur ne devrait pas être supprimé."


def test_unknown_user(user_controller, mock_session):
    """Teste la suppression d'un utilisateur inconnu."""
    initial_count = mock_session.query(User).count()
    user_controller.delete_user(999)
    assert mock_session.query(User).count() == initial_count, "Le nombre d'utilisateurs ne doit pas changer."


def test_create_user_permission_denied(user_controller, monkeypatch):
    """Test que create_user() retourne None si la permission est refusée."""

    monkeypatch.setattr(user_controller, "check_permission", lambda action: False)
    new_user = user_controller.create_user()
    assert new_user is None, "L'utilisateur ne devrait pas être créé."


def test_check_permission_accept(user_controller):
    """Test que check_permission() accepte une permission valide."""
    result = user_controller.check_permission("create_user")
    assert result is True, "La permission devrait être acceptée."


def test_check_permission_refus(user_controller, capsys):
    """Test que check_permission() affiche un message d'erreur en cas de refus de permission."""
    result = user_controller.check_permission("upgrade_user")
    assert result is False, "La permission devrait être refusée."
    captured = capsys.readouterr()
    assert "⛔ Permission refusée" in captured.out, "Le message d'erreur devrait être affiché."


def test_create_user_with_invalid_role(user_controller, mock_session, role_gestion, monkeypatch):
    """Teste la création d'un utilisateur avec un rôle invalide."""
    monkeypatch.setattr(user_controller.view, "choose_role", lambda: "unknown_role")
    new_user = user_controller.create_user()
    assert new_user is None, "L'utilisateur ne devrait pas être créé."


def test_list_users(user_controller, mock_session, sample_user, monkeypatch):
    """Test que list_users() affiche les utilisateurs si l'utilisateur a la permission."""

    monkeypatch.setattr(user_controller, "check_permission", lambda action: True)
    user2 = User(name="Alice", email="alice@example.com", password="pass1", role_id=sample_user.role_id)
    user3 = User(name="Bob", email="bob@example.com", password="pass2", role_id=sample_user.role_id)
    mock_session.add_all([user2, user3])
    mock_session.commit()
    displayed_users = []
    monkeypatch.setattr(user_controller.view, "display_users", lambda users: displayed_users.extend(users))
    user_controller.list_users()
    users = mock_session.query(User).all()
    assert len(displayed_users) == len(users)


def test_list_users_permission_denied(user_controller, monkeypatch):
    """Test que list_users() retourne None si l'utilisateur n'a pas la permission et n'affiche rien."""
    monkeypatch.setattr(user_controller, "check_permission", lambda action: False)
    assert user_controller.list_users() is None, "La liste des utilisateurs ne doit pas être affichée."
