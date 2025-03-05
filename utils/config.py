import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path)

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
SENTRY = os.getenv("SENTRY")

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

if SENTRY:
    try:
        sentry_sdk.init(
            dsn=SENTRY,
            integrations=[SqlalchemyIntegration()],
            traces_sample_rate=1,
            send_default_pii=False,
        )
        print("✅ Sentry activé avec Sqlalchemy")
    except Exception as e:
        print(f"❌ Erreur d'initialisation de Sentry : {e}")
