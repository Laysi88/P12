import pytest
from view.auth_view import AuthView


@pytest.fixture
def auth_view():
    """Fixture qui retourne une instance de AuthView."""
    return AuthView()


def test_prompt_credentials(auth_view, monkeypatch):
    """Test que prompt_credentials() récupère bien les identifiants."""

    inputs = iter(["user@example.com", "securepass"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    email, password = auth_view.prompt_credentials()

    assert email == "user@example.com", "L'email saisi doit être retourné."
    assert password == "securepass", "Le mot de passe saisi doit être retourné."


def test_display_success_message(auth_view, capsys):
    """Test que display_success_message() affiche un message de succès."""

    auth_view.display_success_message("Connexion réussie !")
    captured = capsys.readouterr()
    assert "Connexion réussie !" in captured.out, "Le message de succès doit être affiché."


def test_display_error_message(auth_view, capsys):
    """Test que display_error_message() affiche un message d'erreur."""

    auth_view.display_error_message("Échec de connexion !")
    captured = capsys.readouterr()
    assert "Échec de connexion !" in captured.out, "Le message d'erreur doit être affiché."
