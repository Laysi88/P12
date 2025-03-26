import pytest
from view.menu_view import show_user_menu
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application.current import create_app_session


@pytest.mark.parametrize("user_input", ["1", "2", "3", "4", "5", "0", "X"])
def test_show_user_menu_output(sample_user, capsys, sample_controller, monkeypatch, user_input):
    """Test du menu utilisateur avec plusieurs entrées"""

    with create_pipe_input() as pipe_input:
        if user_input == "1":
            pipe_input.send_text("1\n0\n")
        elif user_input == "2":
            pipe_input.send_text("2\n0\n")
        elif user_input == "3":
            pipe_input.send_text("3\n1\n0\n")
            monkeypatch.setattr("builtins.input", lambda _: "1")
            monkeypatch.setattr(
                sample_controller["user"], "get_user_details", lambda x: print(f"✅ DEBUG: Affichage utilisateur {x}")
            )
        elif user_input in ["4", "5"]:
            pipe_input.send_text(f"{user_input}\n1\n0\n")
        else:
            pipe_input.send_text(f"{user_input}\n0\n")

        print(f"\n🟡 DEBUG: Entrées simulées -> {repr(pipe_input)}\n")

        monkeypatch.setattr("prompt_toolkit.input.defaults.create_input", lambda: pipe_input)
        monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: DummyOutput())
        monkeypatch.setattr("prompt_toolkit.input.typeahead.get_typeahead", lambda x: [])

        session = PromptSession()

        with create_app_session(input=pipe_input, output=DummyOutput()):
            monkeypatch.setattr("prompt_toolkit.shortcuts.prompt", session.prompt)

            if user_input == "3":
                monkeypatch.setattr("builtins.input", lambda _: "1")
            else:
                monkeypatch.setattr("builtins.input", lambda _: "0")

            show_user_menu(sample_user, sample_controller)

    captured = capsys.readouterr()
    output = captured.out

    assert "=== Gestion des utilisateurs ===" in output

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
    elif user_input == "X":
        assert "⚠ Option invalide, essayez encore !" in output


@pytest.mark.parametrize("user_input", ["3"])
def test_show_user_menu_break_after_user_details(sample_user, capsys, sample_controller, monkeypatch, user_input):
    """Vérifie que le break après l'affichage des détails utilisateur est bien couvert."""

    print("\n🟡 DEBUG: Test break après affichage des détails utilisateur lancé\n")

    with create_pipe_input() as pipe_input:
        pipe_input.send_text("3\n0\n")
        monkeypatch.setattr("builtins.input", lambda _: "0")

        monkeypatch.setattr("prompt_toolkit.input.defaults.create_input", lambda: pipe_input)
        monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: DummyOutput())

        with create_app_session(input=pipe_input, output=DummyOutput()):
            show_user_menu(sample_user, sample_controller)

    captured = capsys.readouterr()
    output = captured.out

    assert "Information sur un utilisateur" in output
    assert "=== Gestion des utilisateurs ===" in output


@pytest.mark.parametrize("user_input", ["3", "4", "5"])
def test_show_user_menu_invalid_id(sample_user, capsys, sample_controller, monkeypatch, user_input):
    """Vérifie que l'entrée d'un ID invalide déclenche bien un ValueError et affiche le message d'erreur."""

    with create_pipe_input() as pipe_input:
        pipe_input.send_text(f"{user_input}\nX\n0\n")

        monkeypatch.setattr("builtins.input", lambda _: "X")

        monkeypatch.setattr("prompt_toolkit.input.defaults.create_input", lambda: pipe_input)
        monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: DummyOutput())

        with create_app_session(input=pipe_input, output=DummyOutput()):
            show_user_menu(sample_user, sample_controller)

    captured = capsys.readouterr()
    output = captured.out

    assert "⚠ ID invalide, veuillez entrer un nombre." in output
