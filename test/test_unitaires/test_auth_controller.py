import pytest
import jwt
from controller.auth_controller import AuthController
import datetime
from datetime import timezone


TEST_SECRET_KEY = "test_secret_key"


@pytest.fixture
def auth_controller(monkeypatch, mock_session):
    """Fixture qui retourne une instance de AuthController avec SECRET_KEY et DBSession patchés."""
    monkeypatch.setattr("controller.auth_controller.SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setattr("controller.auth_controller.Session", lambda: mock_session)

    return AuthController()


def test_generate_token(auth_controller, sample_user):
    """Test de la méthode generate_token."""
    token = auth_controller.generate_token(sample_user)
    payload = auth_controller.decode_token(token)

    assert payload is not None, "Le token doit être décodé correctement."
    assert payload["user_id"] == sample_user.id


def test_decode_valid_token(auth_controller, sample_user):
    """Test que decode_token() fonctionne avec un token valide."""
    token = auth_controller.generate_token(sample_user)
    decoded_payload = auth_controller.decode_token(token)

    assert decoded_payload is not None, "Le token valide devrait être décodé."
    assert decoded_payload["user_id"] == sample_user.id


def test_decode_expired_token(auth_controller, capsys, sample_user, monkeypatch):
    """Test que decode_token() renvoie None si le token est expiré."""
    monkeypatch.setattr("controller.auth_controller.datetime", datetime)
    payload = {
        "user_id": sample_user.id,
        "exp": datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=1),
        "role": sample_user.role.name if sample_user.role else None,
    }
    token = jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")
    decoded_payload = auth_controller.decode_token(token)
    assert decoded_payload is None, "Un token expiré doit retourner None."
    captured = capsys.readouterr()
    assert "❌ Token expiré" in captured.out, "Le message d'erreur doit être affiché."


def test_invalid_token(auth_controller, capsys):
    """Test de la méthode decode_token avec un token invalide."""
    token = "invalid_token"
    payload = auth_controller.decode_token(token)
    assert payload is None, "Un token invalide doit retourner None."
    captured = capsys.readouterr()
    assert "❌ Token invalide" in captured.out, "Le message d'erreur doit être affiché."


def test_store_token(mocker, auth_controller):
    """Test que store_token écrit correctement le token dans un fichier."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    test_token = "test_jwt_token"
    auth_controller.store_token(test_token)
    mock_open.assert_called_once_with(".token", "w")
    mock_open().write.assert_called_once_with(test_token)


def test_store_token_bytes(mocker, auth_controller):
    """Test que store_token gère un token en bytes et l'écrit en string."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    test_token = b"test_jwt_token_bytes"
    auth_controller.store_token(test_token)
    mock_open().write.assert_called_once_with("test_jwt_token_bytes")


def test_load_token_success(mocker, auth_controller):
    """Test que load_token charge correctement un token existant."""

    test_token = "test_jwt_token"
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=test_token))
    loaded_token = auth_controller.load_token()
    mock_open.assert_called_once_with(".token", "r")  # Vérifie que le fichier est bien ouvert en mode lecture
    assert loaded_token == test_token, "Le token chargé doit correspondre au contenu du fichier"


def test_load_token_file_not_found(mocker, auth_controller):
    """Test que load_token retourne None si le fichier .token n'existe pas."""
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    loaded_token = auth_controller.load_token()
    assert loaded_token is None, "load_token() doit retourner None si le fichier .token n'existe pas"
