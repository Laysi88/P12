import pytest
from view.auth_view import AuthView
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output.defaults import DummyOutput


@pytest.fixture
def auth_view():
    """Fixture qui retourne une instance de AuthView."""
    return AuthView()


def test_prompt_credentials_with_prompt_toolkit(auth_view, monkeypatch):
    """Test que `prompt_toolkit.prompt()` est bien exécuté sans erreur dans un environnement de test avec `monkeypatch`."""

    monkeypatch.setattr("builtins.input", lambda _: "user@example.com")
    monkeypatch.setattr("prompt_toolkit.shortcuts.PromptSession.prompt", lambda *args, **kwargs: "securepass")
    monkeypatch.setattr("prompt_toolkit.input.defaults.create_input", lambda: create_pipe_input())
    monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: DummyOutput())

    email, password = auth_view.prompt_credentials()

    assert email == "user@example.com", "L'email saisi doit être retourné."
    assert password == "securepass", "Le mot de passe doit être retourné correctement."


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
