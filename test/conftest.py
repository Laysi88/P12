import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Role, User, Client, Event, Contrat  # noqa: F401
from utils.config import Base

# Création de l'engine global pour éviter la recréation multiple
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True)

# Création de la session factory pour les tests
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def session():
    """Fixture pour fournir une session de test isolée à chaque test."""
    Base.metadata.create_all(engine)  # Crée les tables avant chaque test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)  # Nettoie la base après chaque test


@pytest.fixture
def mock_session(monkeypatch, session):
    """Fixture qui remplace la session globale par la session de test."""
    monkeypatch.setattr("utils.config.Session", lambda: session)
    return session


@pytest.fixture
def sample_user():
    """Fixture qui retourne une instance de User."""
    return User(name="John Doe", email="john@example.com", password="securepass", role_id=1)
