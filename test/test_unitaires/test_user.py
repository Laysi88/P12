def test_user_init(sample_user):
    """Test la création d'un utilisateur."""
    assert sample_user.name == "John Doe"
    assert sample_user.email == "john@example.com"
    assert sample_user.password is not None  # Vérifie que set_password() a bien fonctionné
    assert sample_user.role_id == 1


def password_is_hashed(sample_user):
    """Test que le mot de passe est bien hashé."""
    assert sample_user.password != "securepass"


def test_check_password(sample_user):
    """Test la vérification du mot de passe."""
    assert sample_user.check_password("securepass") is True
    assert sample_user.check_password("wrongpass") is False
