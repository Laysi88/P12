from model.role import Role
from model.user import User
from utils.populate_database import seed_roles, seed_admin_user
from sqlalchemy.exc import SQLAlchemyError


def test_seed_admin_user(mock_session):
    """Teste la création d'un administrateur si inexistant."""

    assert mock_session.query(User).filter_by(email="admin@admin.com").first() is None
    gestion_role = Role(name="gestion")
    mock_session.add(gestion_role)
    mock_session.commit()
    seed_admin_user(mock_session)
    admin_user = mock_session.query(User).filter_by(email="admin@admin.com").first()
    assert admin_user is not None
    assert admin_user.name == "Admin"
    assert admin_user.role_id == gestion_role.id


def test_seed_admin_user_already_exists(mock_session, capsys):
    """Vérifie que l'admin n'est pas recréé s'il existe déjà."""

    gestion_role = Role(name="gestion")
    admin_user = User(name="Admin", email="admin@admin.com", password="admin123", role_id=gestion_role.id)
    mock_session.add_all([gestion_role, admin_user])
    mock_session.commit()
    seed_admin_user(mock_session)
    captured = capsys.readouterr()
    assert "✅ Administrateur ajouté" not in captured.out
    assert mock_session.query(User).filter_by(email="admin@admin.com").count() == 1


def test_seed_admin_user_no_gestion_role(mock_session, capsys):
    """Vérifie que l'admin n'est pas créé si le rôle 'gestion' est absent."""

    seed_admin_user(mock_session)
    captured = capsys.readouterr()
    assert "⚠️ Aucun rôle 'gestion' trouvé. Création annulée." in captured.out
    assert mock_session.query(User).filter_by(email="admin@admin.com").first() is None


def test_seed_admin_user_sqlalchemy_error(mocker, capsys):
    """Simule une erreur SQLAlchemy et vérifie que rollback est bien appelé."""

    mock_session = mocker.MagicMock()
    mock_session.query.side_effect = SQLAlchemyError("Erreur simulée")
    seed_admin_user(mock_session)
    mock_session.rollback.assert_called_once()
    captured = capsys.readouterr()
    assert "❌ Erreur lors de l'insertion de l'admin" in captured.out


def test_seed_roles(mock_session):
    """Teste la création des rôles si inexistants."""
    assert mock_session.query(Role).count() == 0
    seed_roles(mock_session)
    roles_in_db = {role.name for role in mock_session.query(Role).all()}
    expected_roles = {"commercial", "gestion", "support"}

    assert roles_in_db == expected_roles


def test_seed_roles_all_exist(mock_session, capsys):
    """Vérifie que la fonction ne fait rien si tous les rôles existent déjà."""

    existing_roles = [Role(name="support"), Role(name="commercial"), Role(name="gestion")]
    mock_session.add_all(existing_roles)
    mock_session.commit()
    seed_roles(mock_session)
    captured = capsys.readouterr()
    assert "Tous les rôles existent déjà." in captured.out
    assert mock_session.query(Role).count() == 3


def test_seed_roles_sqlalchemy_error(mocker, capsys):
    """Simule une erreur SQLAlchemy et vérifie que rollback est bien appelé."""

    mock_session = mocker.MagicMock()
    mock_session.query.side_effect = SQLAlchemyError("Erreur simulée")
    seed_roles(mock_session)
    mock_session.rollback.assert_called_once()
    captured = capsys.readouterr()
    assert "Erreur lors de l'insertion des rôles" in captured.out
