# logic/puc_logic.py
"""
Módulo para la lógica de negocio relacionada con el Plan de Cuentas (PUC).
"""
from typing import List, Dict, Any, Optional
from database import db_manager

def obtener_cuentas(filtro: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Obtiene todas las cuentas del PUC, opcionalmente filtradas.
    Llama a la función correspondiente del gestor de base de datos.
    """
    return db_manager.obtener_cuentas_puc(filtro=filtro)

def obtener_cuenta_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de una cuenta específica por su código.
    """
    return db_manager.obtener_cuenta_puc_por_codigo(codigo)

def agregar_cuenta(codigo: str, nombre: str, naturaleza: str, clase: str, grupo_niif: Optional[str] = None) -> bool:
    """
    Agrega una nueva cuenta al plan.
    Realiza validaciones de negocio si fueran necesarias antes de llamar a la BD.
    """
    # Aquí podrían ir validaciones de negocio, por ahora llama directo a la BD
    return db_manager.agregar_cuenta_puc(codigo, nombre, naturaleza, clase, grupo_niif)

def actualizar_cuenta(codigo: str, nombre: str, naturaleza: str, clase: str, grupo_niif: Optional[str] = None) -> bool:
    """
    Actualiza una cuenta existente.
    """
    return db_manager.actualizar_cuenta_puc(codigo, nombre, naturaleza, clase, grupo_niif)

def eliminar_cuenta(codigo: str) -> bool:
    """
    Elimina una cuenta del plan.
    """
    # La lógica de verificación de si la cuenta está en uso ya está en db_manager,
    # lo cual es bueno.
    return db_manager.eliminar_cuenta_puc(codigo)
