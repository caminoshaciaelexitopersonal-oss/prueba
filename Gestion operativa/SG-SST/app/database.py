import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Configuration for SQLite ---
# Using a file-based SQLite database. No server needed.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sgsst.db"

# Crear el motor de la base de datos
# The connect_args are recommended for SQLite to allow multi-threaded access.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear una clase de sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para los modelos declarativos
Base = declarative_base()

def get_db():
    """
    Función para obtener una sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables():
    """
    Crea todas las tablas en la base de datos.
    """
    Base.metadata.create_all(bind=engine)

print("Configuración de la base de datos cambiada a SQLite.")
