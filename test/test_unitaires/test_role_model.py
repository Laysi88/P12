import pytest
from model.role import Role


@pytest.mark.parametrize(
    "role_name, expected_permissions",
    [
        (
            "gestion",
            {
                "create_user",
                "read_user",
                "update_user",
                "delete_user",
                "read_client",
                "read_contrat",
                "create_contrat",
                "update_contrat",
                "read_contrat",
                "filter_contrat",
                "read_event",
                "filter_event",
                "update_event",
            },
        ),
        (
            "commercial",
            {
                "read_user",
                "create_client",
                "read_client",
                "read_client_personnal",
                "update_client",
                "create_contrat",
                "read_contrat",
                "update_contrat",
                "read_contrat",
                "filter_contrat",
                "create_event",
                "read_event",
            },
        ),
        (
            "support",
            {
                "read_user",
                "read_client",
                "read_contrat",
                "read_event",
                "filter_event",
                "update_event",
            },
        ),
    ],
)
def test_get_permissions(role_name, expected_permissions):
    """Test que get_permissions() retourne les bonnes permissions pour chaque rôle."""
    role = Role(name=role_name)
    assert role.get_permissions() == expected_permissions


def test_has_permission():
    """Test que has_permission() retourne True si le rôle a la permission."""
    role = Role(name="gestion")
    assert role.has_permission("create_user") is True


def test_not_has_permission():
    """Test que has_permission() retourne False si le rôle n'a pas la permission."""
    role = Role(name="commercial")
    assert role.has_permission("create_user") is False


def test_unknown_permission():
    """Test que has_permission() retourne False pour une action inconnue."""
    role = Role(name="gestion")
    assert role.has_permission("delete_client") is False


def test_unknown_role():
    """Test que get_permissions() retourne un set vide pour un rôle inconnu."""
    role = Role(name="random_role")
    assert role.get_permissions() == set()
