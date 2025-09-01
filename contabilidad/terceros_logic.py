# logic/terceros_logic.py
"""
Módulo para la lógica de negocio relacionada con los Terceros (clientes, proveedores, etc.).
"""
from typing import List, Dict, Any
from database import db_manager

def get_clientes() -> List[Dict[str, Any]]:
    """
    Obtiene una lista de todos los terceros que son clientes.
    """
    return db_manager.obtener_terceros_por_tipo('Cliente')

def get_proveedores() -> List[Dict[str, Any]]:
    """
    Obtiene una lista de todos los terceros que son proveedores.
    """
    return db_manager.obtener_terceros_por_tipo('Proveedor')
