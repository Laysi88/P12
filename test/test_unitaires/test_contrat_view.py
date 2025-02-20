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

    inputs = iter(["12000", "3000", "oui"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    new_total, new_remaining, new_status = contrat_view.input_update_contrat_info(contrat)

    assert new_total == 12000
    assert new_remaining == 3000
    assert new_status is True


def test_input_contrat_info_invalid_id(contrat_view, mock_session, monkeypatch):
    """Test que input_contrat_info affiche un message d'erreur en cas d'ID invalide."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)

    fake_clients = [client]

    inputs = iter(["99", str(client.id), "10000", "5000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    error_message = []
    monkeypatch.setattr("builtins.print", lambda msg: error_message.append(msg))

    contrat_view.input_contrat_info(fake_clients)

    assert "❌ ID invalide. Veuillez entrer un ID existant." in error_message, "Le message d'erreur doit s'afficher."


def test_input_contrat_info_invalid_value(contrat_view, mock_session, monkeypatch):
    """Test que input_contrat_info affiche un message d'erreur en cas de valeur non numérique."""

    client = Client(name="Client Test", email="client@test.com")
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)

    fake_clients = [client]

    inputs = iter(["abc", str(client.id), "10000", "5000"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    error_message = []
    monkeypatch.setattr("builtins.print", lambda msg: error_message.append(msg))

    contrat_view.input_contrat_info(fake_clients)

    assert "❌ Veuillez entrer un nombre valide." in error_message, "Le message d'erreur doit s'afficher."
