import pytest
from view.contrat_view import ContratView
from model.client import Client
from model.contrat import Contrat


@pytest.fixture
def contrat_view():
    """Fixture pour instancier la vue des contrats."""
    return ContratView()


def test_display_info_message(contrat_view, capsys):
    """Test que display_info_message affiche correctement un message d'information."""
    contrat_view.display_info_message("Contrat validé !")
    captured = capsys.readouterr()
    assert "ℹ️ Contrat validé !" in captured.out


def test_display_error_message(contrat_view, capsys):
    """Test que display_error_message affiche correctement un message d'erreur."""
    contrat_view.display_error_message("Erreur critique !")
    captured = capsys.readouterr()
    assert "❌ Erreur critique !" in captured.out


def test_input_contrat_info(contrat_view, mock_session, monkeypatch):
    """Test que input_contrat_info capture correctement les entrées utilisateur."""

    client1 = Client(name="Client 1", email="client1@test.com")
    client2 = Client(name="Client 2", email="client2@test.com")

    mock_session.add_all([client1, client2])
    mock_session.commit()

    mock_session.refresh(client1)
    mock_session.refresh(client2)

    clients = [client1, client2]

    inputs = iter([str(client1.id), "10000", "5000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    client_id, total_amount, remaining_amount = contrat_view.input_contrat_info(clients)

    assert client_id == client1.id
    assert total_amount == 10000
    assert remaining_amount == 5000


def test_input_update_contrat_info(contrat_view, mock_session, monkeypatch):
    """Test que input_update_contrat_info capture correctement les entrées utilisateur."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)
    contrat = Contrat(client_id=client.id, total_amount=10000, remaining_amount=5000, status=False)
    mock_session.add(contrat)
    mock_session.commit()
    mock_session.refresh(contrat)

    inputs = iter(["oui", "10000", "3000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    new_total, new_remaining, new_status = contrat_view.input_update_contrat_info(contrat)

    assert new_total == 10000
    assert new_remaining == 3000
    assert new_status is True


def test_input_contrat_info_cancel(contrat_view, mock_session, monkeypatch, capsys):
    """Test que input_contrat_info retourne None lorsque l'utilisateur appuie sur Entrée pour annuler."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)

    fake_clients = [client]

    # ⚠ L'utilisateur appuie sur Entrée directement (input vide)
    inputs = iter([""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = contrat_view.input_contrat_info(fake_clients)

    captured = capsys.readouterr()

    # ✅ Vérification
    assert result is None, "La fonction doit retourner None si l'utilisateur annule."
    assert "🔙 Retour au menu précédent." in captured.out, "Le message de retour doit s'afficher."


def test_input_contrat_info_invalid_id(contrat_view, mock_session, monkeypatch, capsys):
    """Test que input_contrat_info affiche un message d'erreur en cas d'ID invalide."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)

    fake_clients = [client]

    inputs = iter(["99", str(client.id), "10000", "5000"])  # ID 99 inexistant
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    contrat_view.input_contrat_info(fake_clients)

    captured = capsys.readouterr()

    assert "❌ ID invalide." in captured.out, "Le message d'erreur doit s'afficher."


def test_input_contrat_info_invalid_value(contrat_view, mock_session, monkeypatch, capsys):
    """Test que input_contrat_info affiche un message d'erreur en cas de valeur non numérique."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)

    fake_clients = [client]

    inputs = iter(["1", str(client.id), "abc", "5000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    contrat_view.input_contrat_info(fake_clients)

    captured = capsys.readouterr()

    assert "❌ Montant invalide." in captured.out, "Le message d'erreur doit s'afficher."


def test_display_contrats(contrat_view, capsys, mock_session, sample_client):
    """Test que display_contrats affiche correctement les contrats."""

    contrat_1 = Contrat(client_id=sample_client.id, total_amount=5000, remaining_amount=2000, status=False)
    contrat_2 = Contrat(client_id=sample_client.id, total_amount=7000, remaining_amount=0, status=True)

    mock_session.add_all([contrat_1, contrat_2])
    mock_session.commit()

    contrat_view.display_contrats([contrat_1, contrat_2])

    captured = capsys.readouterr()
    assert f"🔹 ID: {contrat_1.id}" in captured.out, "Le premier contrat doit être affiché."
    assert f"🔹 ID: {contrat_2.id}" in captured.out, "Le deuxième contrat doit être affiché."
    assert "📜 Liste des contrats :" in captured.out, "Le titre doit être affiché."


def test_no_contrat_to_display(contrat_view, capsys):
    """Test que display_contrats affiche un message si aucun contrat n'est à afficher."""

    contrat_view.display_contrats([])

    captured = capsys.readouterr()
    assert "📭 Aucun contrat à afficher." in captured.out, "Le message doit être affiché."


def test_ask_filter_option(contrat_view, monkeypatch):
    """Test que ask_filter_option retourne le bon filtre selon l'entrée utilisateur."""

    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert contrat_view.ask_filter_option() == "non_signes", "Le choix 1 doit retourner 'non_signes'"

    monkeypatch.setattr("builtins.input", lambda _: "2")
    assert contrat_view.ask_filter_option() == "paiement_en_attente", "Le choix 2 doit retourner 'paiement_en_attente'"

    monkeypatch.setattr("builtins.input", lambda _: "3")
    assert contrat_view.ask_filter_option() is None, "Un choix invalide doit retourner None"

    monkeypatch.setattr("builtins.input", lambda _: "abc")
    assert contrat_view.ask_filter_option() is None, "Une entrée non numérique doit retourner None"
