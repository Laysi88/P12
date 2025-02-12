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
    mock_open.assert_called_once_with(".token", "r")
    assert loaded_token == test_token, "Le token chargé doit correspondre au contenu du fichier"


def test_load_token_file_not_found(mocker, auth_controller):
    """Test que load_token retourne None si le fichier .token n'existe pas."""
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    loaded_token = auth_controller.load_token()
    assert loaded_token is None, "load_token() doit retourner None si le fichier .token n'existe pas"


def test_login_success(auth_controller, mocker, sample_user, monkeypatch):
    """Test de la connexion réussie avec les bons identifiants."""

    monkeypatch.setattr(auth_controller.view, "prompt_credentials", lambda: (sample_user.email, "securepass"))
    mock_generate_token = mocker.patch.object(auth_controller, "generate_token", return_value="mock_token")
    mock_store_token = mocker.patch.object(auth_controller, "store_token")
    mock_display_success = mocker.patch.object(auth_controller.view, "display_success_message")
    token = auth_controller.login()
    assert token == "mock_token", "Un token doit être retourné en cas de connexion réussie."
    mock_generate_token.assert_called_once_with(sample_user)
    mock_store_token.assert_called_once_with("mock_token")
    mock_display_success.assert_called_once_with(f"✅ Connexion réussie ! Bienvenue {sample_user.name}.")


def test_login_invalid_credentials(auth_controller, mocker, sample_user, monkeypatch):
    """Test de la connexion avec des identifiants invalides."""
    monkeypatch.setattr(auth_controller.view, "prompt_credentials", lambda: (sample_user.email, "wrongpass"))
    mock_generate_token = mocker.patch.object(auth_controller, "generate_token", return_value="mock_token")
    mock_store_token = mocker.patch.object(auth_controller, "store_token")
    mock_display_error = mocker.patch.object(auth_controller.view, "display_error_message")
    token = auth_controller.login()
    assert token is None, "Aucun token ne doit être retourné en cas d'erreur d'authentification."
    mock_generate_token.assert_not_called()
    mock_store_token.assert_not_called()
    mock_display_error.assert_called_once_with("❌ Échec de connexion. Vérifiez vos identifiants.")


def test_verify_token_valid(auth_controller, mock_session, mocker, sample_user):
    """Test de verify_token avec un token valide."""

    valid_token = auth_controller.generate_token(sample_user)
    mocker.patch.object(auth_controller, "load_token", return_value=valid_token)
    mocker.patch.object(auth_controller, "decode_token", return_value={"user_id": sample_user.id})
    user = auth_controller.verify_token()
    assert user is not None, "L'utilisateur doit être retourné si le token est valide."
    assert user.id == sample_user.id, "L'utilisateur retourné doit être celui du token."


def test_verify_token_no_token(auth_controller, mocker):
    """Test de verify_token lorsqu'aucun token n'est stocké."""

    mocker.patch.object(auth_controller, "load_token", return_value=None)
    mock_display_error = mocker.patch.object(auth_controller.view, "display_error_message")
    user = auth_controller.verify_token()
    assert user is None, "Aucun utilisateur ne doit être retourné si le token est absent."
    mock_display_error.assert_called_once_with("⚠️ Vous devez vous connecter !")


def test_verify_token_invalid(auth_controller, mocker):
    """Test de verify_token avec un token invalide."""

    mocker.patch.object(auth_controller, "load_token", return_value="invalid_token")
    mocker.patch.object(auth_controller, "decode_token", return_value=None)
    user = auth_controller.verify_token()
    assert user is None, "Aucun utilisateur ne doit être retourné si le token est invalide."


def test_verify_token_user_not_found(auth_controller, mock_session, mocker):
    """Test de verify_token lorsque l'utilisateur du token n'existe plus."""

    mocker.patch.object(auth_controller, "load_token", return_value="valid_token")
    mocker.patch.object(auth_controller, "decode_token", return_value={"user_id": 999})
    mock_display_error = mocker.patch.object(auth_controller.view, "display_error_message")
    user = auth_controller.verify_token()
    assert user is None, "Aucun utilisateur ne doit être retourné si l'utilisateur du token n'existe pas."
    mock_display_error.assert_called_once_with("⚠️ Utilisateur introuvable.")


def test_logout(auth_controller, mocker):
    """Test de la méthode logout."""
    mock_display_success = mocker.patch.object(auth_controller.view, "display_success_message")
    auth_controller.logout()
    mock_display_success.assert_called_once_with("👋 Déconnexion réussie.")
