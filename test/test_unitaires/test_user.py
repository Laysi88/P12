def test_user_init(sample_user):
    """Test la création d'un utilisateur."""
    assert sample_user.name == "John Doe"
    assert sample_user.email == "john@example.com"
    assert sample_user.password is not None
    assert sample_user.role_id == 1


def password_is_hashed(sample_user):
    """Test que le mot de passe est bien hashé."""
    assert sample_user.password != "securepass"


def test_check_password(sample_user):
    """Test la vérification du mot de passe."""
    assert sample_user.check_password("securepass") is True
    assert sample_user.check_password("wrongpass") is False


def test_user_repr(sample_user):
    """Test la représentation textuelle (__repr__) de l'utilisateur."""
    expected_repr = f"<User(id={sample_user.id}, name={sample_user.name}, email={sample_user.email}, role_id={sample_user.role_id})>"
    assert repr(sample_user) == expected_repr
