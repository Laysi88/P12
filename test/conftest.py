import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Role, User, Client, Event, Contrat  # noqa: F401
from controller import UserController, ClientController, ContratController, EventController
from utils.config import Base
from datetime import datetime


TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def session():
    """Fixture pour une session isolée en SQLite."""
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mock_session(monkeypatch, session):
    """Fixture qui remplace la session globale par la session de test."""
    monkeypatch.setattr("utils.config.Session", lambda: session)
    return session


@pytest.fixture
def role_gestion(mock_session):
    """Fixture pour un rôle 'gestion'."""
    role = Role(name="gestion")
    mock_session.add(role)
    mock_session.commit()
    mock_session.refresh(role)
    return role


@pytest.fixture
def role_commercial(mock_session):
    """Fixture pour un rôle 'commercial'."""
    role = Role(name="commercial")
    mock_session.add(role)
    mock_session.commit()
    mock_session.refresh(role)
    return role


@pytest.fixture
def role_support(mock_session):
    """Fixture pour un rôle 'support'."""
    role = Role(name="support")
    mock_session.add(role)
    mock_session.commit()
    mock_session.refresh(role)
    return role


@pytest.fixture
def sample_user(role_gestion, mock_session):
    """Fixture qui retourne un utilisateur avec un rôle 'gestion'."""
    user = User(name="John Doe", email="john@example.com", password="securepass", role_id=role_gestion.id)
    mock_session.add(user)
    mock_session.commit()
    mock_session.refresh(user)
    return user


@pytest.fixture
def sample_support(role_support, mock_session):
    """Fixture qui retourne un utilisateur avec un rôle 'support'."""
    user = User(name="Bob", email="bob@exemple.com", password="securepass", role_id=role_support.id)
    mock_session.add(user)
    mock_session.commit()
    mock_session.refresh(user)
    return user


@pytest.fixture
def sample_commercial(role_commercial, mock_session):
    """Fixture qui retourne un utilisateur avec un rôle 'commercial'."""
    user = User(name="Alice", email="alice@example.com", password="securepass", role_id=role_commercial.id)
    mock_session.add(user)
    mock_session.commit()
    mock_session.refresh(user)
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
def sample_contrat(sample_client, mock_session):
    """Fixture qui retourne un contrat fictif associé à un client existant."""
    contrat = Contrat(
        client_id=sample_client.id,
        total_amount=10000,
        remaining_amount=5000,
        status=False,
    )
    mock_session.add(contrat)
    mock_session.commit()
    mock_session.refresh(contrat)
    return contrat


@pytest.fixture
def sample_event(sample_contrat, mock_session):
    """Fixture qui retourne un événement fictif associé à un contrat signé."""

    sample_contrat.status = True
    mock_session.commit()

    event = Event(
        name="Événement Test",
        contrat_id=sample_contrat.id,
        start_date=datetime(2025, 3, 15, 10, 0),
        end_date=datetime(2025, 3, 15, 18, 0),
        location="Paris",
        attendees=50,
        support_id=None,
        notes="Événement de démonstration.",
    )

    mock_session.add(event)
    mock_session.commit()
    mock_session.refresh(event)
    return event


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
