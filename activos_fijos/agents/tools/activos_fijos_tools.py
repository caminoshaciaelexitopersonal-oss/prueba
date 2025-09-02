# activos_fijos/agents/tools/activos_fijos_tools.py

"""
Este archivo centraliza las herramientas tácticas que los agentes del módulo de Activos Fijos pueden utilizar.
"""

# Importar las herramientas de la lógica de activos fijos
from activos_fijos.logic import (
    registrar_activo,
    ejecutar_proceso_depreciacion_mensual,
)

# Para que el agente de activos fijos pueda consultar el PUC,
# también necesita las herramientas de consulta de cuentas.
from contabilidad.puc_logic import obtener_cuentas, obtener_cuenta_por_codigo

# Lista de todas las herramientas disponibles para el agente de activos fijos
activos_fijos_tools = [
    registrar_activo,
    ejecutar_proceso_depreciacion_mensual,
    obtener_cuentas,
    obtener_cuenta_por_codigo,
]
