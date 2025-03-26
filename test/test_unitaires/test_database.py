from sqlalchemy import text


def test_database_type(session):
    """Teste le type de la base de données"""

    db_url = str(session.bind.url)
    assert "sqlite" in db_url, f"❌ Type de base de données incorrect: {db_url}"


def test_database_connection(session):
    """Teste la connexion à la base de données SQLite"""
    with session.connection() as connection:
        result = connection.execute(text("SELECT 1")).scalar()
        assert result == 1
        print("✅ Connexion à la base de données SQLite réussie")
