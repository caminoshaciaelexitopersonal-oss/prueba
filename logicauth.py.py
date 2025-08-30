# logic/auth.py
import bcrypt
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña."""
    try:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    except Exception as e:
        logger.error(f"Error al hashear contraseña: {e}")
        raise ValueError("Error interno al procesar la contraseña.") from e

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    if not stored_hash or not provided_password:
        return False
    try:
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
    except ValueError as e:
        # Podría ocurrir si el hash almacenado no tiene el formato esperado por bcrypt
        logger.warning(f"Error al verificar contraseña (posible hash inválido): {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al verificar contraseña: {e}")
        return False