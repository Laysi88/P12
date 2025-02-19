from model.client import Client


def test_client_repr():
    """Test la représentation textuelle (__repr__) d'un client."""

    client = Client(
        name="Client X", email="client@business.com", phone="123456789", company="Business Corp", commercial_id=42
    )

    expected_repr = (
        f"<Client(id={client.id}, name=Client X, email=client@business.com, company=Business Corp, commercial_id=42)>"
    )
    assert repr(client) == expected_repr, "La méthode __repr__ ne retourne pas la bonne chaîne."
