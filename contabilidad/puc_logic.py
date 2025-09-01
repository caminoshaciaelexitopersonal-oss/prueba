# logic/puc_logic.py
"""
Módulo para la lógica de negocio relacionada con el Plan de Cuentas (PUC).
"""
from typing import List, Dict, Any, Optional
from database import db_manager
from langchain_core.tools import tool

@tool
def obtener_cuentas(filtro: Optional[str] = None) -> str:
    """
    Busca y obtiene cuentas del Plan Único de Cuentas (PUC).

    Esta herramienta es esencial para encontrar los códigos de cuenta correctos antes de registrar un comprobante.
    Puedes usarla para encontrar una cuenta por su nombre o código.

    Args:
        filtro (Optional[str]): Un término de búsqueda para filtrar las cuentas. Puede ser parte del código (ej: '1105') o del nombre (ej: 'caja'). Si se omite, devuelve las primeras cuentas del plan.

    Returns:
        str: Una cadena formateada con la lista de cuentas encontradas, incluyendo su código, nombre y naturaleza (Débito/Crédito). Si no se encuentran, devuelve un mensaje indicándolo.
    """
    cuentas = db_manager.obtener_cuentas_puc(filtro=filtro, limit=20) # Limitar para no abrumar
    if not cuentas:
        return "No se encontraron cuentas con ese filtro."

    # Formatear la salida para que sea fácil de leer para el LLM y el usuario
    headers = ["Código", "Nombre", "Naturaleza"]
    data = [[c['codigo'], c['nombre'], c['naturaleza']] for c in cuentas]

    # Calcular anchos de columna
    widths = [max(len(str(item)) for item in col) for col in zip(headers, *data)]

    header_line = " | ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
    separator = "-+-".join("-" * w for w in widths)
    data_lines = "\n".join(" | ".join(f"{str(item):<{w}}" for item, w in zip(row, widths)) for row in data)

    return f"{header_line}\n{separator}\n{data_lines}"


@tool
def obtener_cuenta_por_codigo(codigo: str) -> str:
    """
    Obtiene los datos de una cuenta específica por su código exacto.

    Útil para verificar si un código de cuenta existe antes de usarlo en una transacción.

    Args:
        codigo (str): El código exacto de la cuenta a buscar (ej: '110505').

    Returns:
        str: Los detalles de la cuenta si se encuentra, o un mensaje indicando que no existe.
    """
    cuenta = db_manager.obtener_cuenta_puc_por_codigo(codigo)
    if cuenta:
        return f"Cuenta encontrada: Código: {cuenta['codigo']}, Nombre: {cuenta['nombre']}, Naturaleza: {cuenta['naturaleza']}"
    else:
        return f"Error: No se encontró ninguna cuenta con el código exacto '{codigo}'."

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
