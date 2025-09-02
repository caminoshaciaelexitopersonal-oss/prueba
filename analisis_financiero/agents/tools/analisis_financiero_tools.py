# analisis_financiero/agents/tools/analisis_financiero_tools.py

"""
Este archivo centraliza las herramientas tácticas que los agentes del módulo de Análisis Financiero pueden utilizar.
"""

# Importar las herramientas de la lógica de análisis financiero
from analisis_financiero.logic import (
    generar_analisis_financiero_completo,
    generar_historial_de_ratio,
)

# Lista de todas las herramientas disponibles para el agente de análisis financiero
analisis_financiero_tools = [
    generar_analisis_financiero_completo,
    generar_historial_de_ratio,
]
