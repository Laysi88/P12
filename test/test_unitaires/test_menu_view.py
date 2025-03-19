import pytest
from view.menu_view import show_menu, show_user_menu
from rich.console import Console
from controller import UserController, ClientController, ContratController, EventController
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application.current import create_app_session


@pytest.fixture
def sample_console():
    """Fixture pour initialiser un objet Console."""
    return Console(force_terminal=False, force_interactive=False)


@pytest.fixture
def sample_controller(sample_user):
    """Fixture pour initialiser un objet Controller."""
    controllers = {
        "user": UserController(sample_user),
        "client": ClientController(sample_user),
        "contrat": ContratController(sample_user),
        "event": EventController(sample_user),
    }
    return controllers


def test_show_menu_output(sample_user, capsys):
    """Test que `show_menu()` affiche bien le menu principal sans formatage de Rich."""

    show_menu(sample_user)

    captured = capsys.readouterr()
    output = captured.out

    assert f"🔐 Connecté en tant que {sample_user.name} - {sample_user.role.name}" in output
    assert "=== Menu Principal ===" in output
    assert "1️⃣ Gérer les utilisateurs" in output
    assert "2️⃣ Gérer les clients" in output
    assert "3️⃣ Gérer les contrats" in output
    assert "4️⃣ Gérer les événements" in output
    assert "0️⃣ Quitter" in output
    assert "🔑 Logout (L)" in output


@pytest.mark.parametrize("user_input", ["1", "2", "3", "4", "5", "0"])
def test_show_user_menu_output(sample_user, capsys, sample_controller, monkeypatch, user_input):
    """Test du menu utilisateur avec plusieurs entrées."""

    with create_pipe_input() as pipe_input:
        # Envoie l'entrée utilisateur + "0" pour quitter le menu
        pipe_input.send_text(f"{user_input}\n0\n")

        monkeypatch.setattr("prompt_toolkit.input.defaults.create_input", lambda: pipe_input)
        monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: DummyOutput())
        monkeypatch.setattr("prompt_toolkit.input.typeahead.get_typeahead", lambda x: [])

        session = PromptSession()

        with create_app_session(input=pipe_input, output=DummyOutput()):
            monkeypatch.setattr("prompt_toolkit.shortcuts.prompt", session.prompt)
            show_user_menu(sample_user, sample_controller)

    captured = capsys.readouterr()
    output = captured.out

    # Vérifier que le menu est bien affiché
    assert "=== Gestion des utilisateurs ===" in output

    # Vérifier que chaque option testée est bien affichée
    if user_input == "1" and sample_user.role.name == "gestion":
        assert "Créer un utilisateur" in output
    elif user_input == "2":
        assert "Lister les utilisateurs" in output
    elif user_input == "3":
        assert "Information sur un utilisateur" in output
    elif user_input == "4" and sample_user.role.name == "gestion":
        assert "Modifier un utilisateur" in output
    elif user_input == "5" and sample_user.role.name == "gestion":
        assert "Supprimer un utilisateur" in output
    elif user_input == "0":
        assert "Retour au menu principal" in output
