from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends

#URL de la base SQLite
DATABASE_URL = "sqlite:///./database/db.sqlite"

# Création du moteur SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session de bases de données
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pour les modéles ORM (traduction de requetes objet en SQL)
Base = declarative_base()

# Injection de la DB dans Fastapi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()