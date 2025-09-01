# analisis_financiero/agents/tools/financial_analysis_tools.py
"""
Herramientas especializadas para que los agentes de análisis financiero puedan interactuar
con la lógica de negocio del sistema.
"""
import json
from typing import Optional
from langchain_core.tools import tool
from .... import logic as analisis_financiero_logic

def _serializar_respuesta(datos) -> str:
    """Función de ayuda para convertir la salida a una cadena JSON."""
    if not datos:
        return "No se encontraron datos."
    return json.dumps(datos, indent=2, ensure_ascii=False)

# --- Herramientas para los Capitanes de Análisis Financiero ---

@tool
def generar_analisis_completo_tool(fecha: str) -> str:
    """
    Genera un análisis financiero completo con todos los ratios (Liquidez, Gestión, Endeudamiento, Rentabilidad, Mercado) para una fecha de corte específica.
    La fecha debe estar en formato 'AAAA-MM-DD'.
    """
    try:
        resultado = analisis_financiero_logic.generar_analisis_financiero_completo(fecha)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió una excepción al generar el análisis completo: {e}"

@tool
def generar_historial_ratio_tool(nombre_ratio: str, categoria_ratio: str, num_meses: int = 6) -> str:
    """
    Genera un historial de un ratio financiero específico para los últimos N meses.
    Debes especificar el 'nombre_ratio' exacto (ej: 'retorno_sobre_patrimonio_roe') y su 'categoria_ratio' (ej: 'Ratios de Rentabilidad').
    """
    try:
        resultado = analisis_financiero_logic.generar_historial_de_ratio(nombre_ratio, categoria_ratio, num_meses)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió una excepción al generar el historial del ratio: {e}"
