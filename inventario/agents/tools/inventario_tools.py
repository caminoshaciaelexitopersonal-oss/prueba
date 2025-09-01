# inventario/agents/tools/inventario_tools.py

"""
Este archivo centraliza las herramientas (herramientas tácticas) que los agentes del módulo de inventario pueden utilizar.
"""

# Importar las herramientas de la lógica de inventario
from inventario.inventario_logic import (
    crear_producto,
    obtener_productos,
    registrar_movimiento_inventario,
)

# Lista de todas las herramientas disponibles para el agente de inventario
inventario_tools = [
    crear_producto,
    obtener_productos,
    registrar_movimiento_inventario,
]
