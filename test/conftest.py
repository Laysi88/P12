import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Role, User, Client, Event, Contrat  # noqa: F401
from utils.config import Base


TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def session():
    """Fixture pour une session isolée en SQLite."""
    Base.metadata.create_all(engine)  # Création des tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)  # Suppression des tables après chaque test


@pytest.fixture
def mock_session(monkeypatch, session):
    """Fixture qui remplace la session globale par la session de test."""
    monkeypatch.setattr("utils.config.Session", lambda: session)
    return session


@pytest.fixture
def role_gestion(session):
    """Fixture pour un rôle 'gestion'."""
    role = Role(name="gestion")
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@pytest.fixture
def role_commercial(session):
    """Fixture pour un rôle 'commercial'."""
    role = Role(name="commercial")
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@pytest.fixture
def role_support(session):
    """Fixture pour un rôle 'support'."""
    role = Role(name="support")
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@pytest.fixture
def sample_user(role_gestion, session):
    """Fixture qui retourne un utilisateur avec un rôle 'gestion'."""
    user = User(name="John Doe", email="john@example.com", password="securepass", role_id=role_gestion.id)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_commercial(role_commercial, session):
    """Fixture qui retourne un utilisateur avec un rôle 'commercial'."""
    user = User(name="Alice", email="alice@example.com", password="securepass", role_id=role_commercial.id)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_client(mock_session, sample_commercial):
    """Fixture qui crée un client attribué à un commercial."""
    client = Client(
        name="Client Test",
        email="client@test.com",
        phone="0101010101",
        company="Test Corp",
        commercial_id=sample_commercial.id,
    )
    mock_session.add(client)
    mock_session.commit()
    mock_session.refresh(client)
    return client


@pytest.fixture
def sample_contrat(sample_client, session):
    """Fixture qui retourne un contrat fictif associé à un client existant."""
    contrat = Contrat(
        client_id=sample_client.id,
        total_amount=10000,
        remaining_amount=5000,
        status=False,
    )
    session.add(contrat)
    session.commit()
    session.refresh(contrat)
    return contrat
