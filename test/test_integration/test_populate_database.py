from model.role import Role
from utils.populate_database import seed_roles
from sqlalchemy.exc import SQLAlchemyError


def test_seed_roles(mock_session):
    assert mock_session.query(Role).count() == 0  # Vérification initiale

    # Exécuter la fonction avec la session du test
    seed_roles(mock_session)

    roles_in_db = {role.name for role in mock_session.query(Role).all()}
    expected_roles = {"commercial", "gestion", "support"}

    assert roles_in_db == expected_roles


def test_seed_roles_all_exist(mock_session, capsys):
    """Vérifie que la fonction ne fait rien si tous les rôles existent déjà."""

    # 1. Préparer la base avec les rôles existants
    existing_roles = [Role(name="support"), Role(name="commercial"), Role(name="gestion")]
    mock_session.add_all(existing_roles)
    mock_session.commit()

    # 2. Exécuter seed_roles()
    seed_roles(mock_session)

    # 3. Capturer l'affichage (stdout)
    captured = capsys.readouterr()

    # 4. Vérifier que le message attendu est bien affiché
    assert "Tous les rôles existent déjà." in captured.out

    # 5. Vérifier qu'aucun rôle supplémentaire n'a été ajouté
    assert mock_session.query(Role).count() == 3


def test_seed_roles_sqlalchemy_error(mocker, capsys):
    """Simule une erreur SQLAlchemy et vérifie que rollback est bien appelé."""

    # 1. Mock de la session SQLAlchemy
    mock_session = mocker.MagicMock()

    # 2. Simuler une erreur SQLAlchemy lors de `query()`
    mock_session.query.side_effect = SQLAlchemyError("Erreur simulée")

    # 3. Appeler la fonction avec la session mockée
    seed_roles(mock_session)

    # 4. Vérifier si `rollback()` a bien été appelé
    mock_session.rollback.assert_called_once()

    # 5. Vérifier que le message d'erreur est bien affiché
    captured = capsys.readouterr()
    assert "Erreur lors de l'insertion des rôles" in captured.out
