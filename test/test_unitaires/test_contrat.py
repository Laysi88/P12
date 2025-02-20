import pytest
from model.contrat import Contrat
from model.client import Client
import re


def test_create_contrat(session):
    """Test la création d'un contrat en base de données."""

    client = Client(name="Entreprise X", email="contact@entreprise.com", phone="0102030405", company="Entreprise X")
    session.add(client)
    session.commit()
    contrat = Contrat(client_id=client.id, total_amount=10000, remaining_amount=5000)
    session.add(contrat)
    session.commit()

    assert contrat.id is not None, "Le contrat doit avoir un ID après l'ajout en BDD."
    assert contrat.date_created is not None, "Le champ date_created doit être rempli automatiquement."
    assert contrat.status is False, "Le contrat ne doit pas être signé par défaut."
    assert contrat.client_id == client.id, "Le contrat doit être rattaché au bon client."


def test_sign_contrat(session):
    """Test que la signature d'un contrat fonctionne."""

    client = Client(name="Client Y", email="clientY@business.com", phone="987654321", company="Tech Corp")
    session.add(client)
    session.commit()
    contrat = Contrat(client_id=client.id, total_amount=15000, remaining_amount=7500)
    session.add(contrat)
    session.commit()

    contrat.sign_contrat()
    session.commit()
    assert contrat.status is True, "Le contrat doit être marqué comme signé après l'appel à sign_contrat()."


def test_repr_contrat(session):
    """Test la représentation textuelle d'un contrat."""

    contrat = Contrat(client_id=1, total_amount=10000, remaining_amount=5000)
    assert isinstance(repr(contrat), str), "Le __repr__ doit retourner une chaîne de caractères."
    pattern = (
        r"<Contrat\(id=None, client_id=1, total_amount=10000(?:\.0)?, remaining_amount=5000(?:\.0)?, "
        r"date_created=[^,]+, status=False\)>"
    )

    assert re.match(pattern, repr(contrat)), f"La représentation textuelle est incorrecte : {repr(contrat)}"


def test_contrat_total_amount_negative(mock_session):
    """Test qu'un contrat ne peut pas avoir un montant total négatif."""
    with pytest.raises(ValueError, match="total_amount ne peut pas être négatif."):
        contrat = Contrat(client_id=1, total_amount=-5000, remaining_amount=2000)
        mock_session.add(contrat)
        mock_session.commit()


def test_contrat_remaining_amount_negative(mock_session):
    """Test qu'un contrat ne peut pas avoir un montant restant négatif."""
    with pytest.raises(ValueError, match="remaining_amount ne peut pas être négatif."):
        contrat = Contrat(client_id=1, total_amount=5000, remaining_amount=-1000)
        mock_session.add(contrat)
        mock_session.commit()


def test_contrat_remaining_greater_than_total(mock_session):
    """Test qu'un contrat ne peut pas avoir un montant restant supérieur au total."""
    with pytest.raises(ValueError, match="Le montant restant ne peut pas dépasser le montant total."):
        contrat = Contrat(client_id=1, total_amount=5000, remaining_amount=6000)
        mock_session.add(contrat)
        mock_session.commit()
