# agents/tools/contabilidad_tools.py
"""
Herramientas especializadas para que el agente de contabilidad pueda interactuar
con la lógica de negocio y la base de datos del sistema contable.
"""
import json
from typing import Optional
from langchain_core.tools import tool
from contabilidad import reportes_logic

def _serializar_respuesta(datos) -> str:
    """Función de ayuda para convertir la salida a una cadena JSON."""
    if not datos:
        return "No se encontraron datos."
    # Convertir a JSON string. El LLM puede procesar esto fácilmente.
    return json.dumps(datos, indent=2, ensure_ascii=False)

@tool
def generar_balance_general_tool(fecha_fin: str) -> str:
    """
    Genera el Balance General (también conocido como Estado de Situación Financiera)
    a una fecha de corte específica. Este reporte muestra Activos, Pasivos y Patrimonio.
    El parámetro 'fecha_fin' debe estar en formato 'AAAA-MM-DD'.
    """
    try:
        resultado = reportes_logic.generar_balance_general(fecha_fin)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió un error al generar el Balance General: {e}"

@tool
def generar_estado_resultados_tool(fecha_inicio: str, fecha_fin: str) -> str:
    """
    Genera el Estado de Resultados (también conocido como Estado de Ganancias y Pérdidas)
    para un rango de fechas. Este reporte muestra Ingresos, Costos y Gastos para calcular la utilidad.
    Los parámetros 'fecha_inicio' y 'fecha_fin' deben estar en formato 'AAAA-MM-DD'.
    """
    try:
        resultado = reportes_logic.generar_estado_resultados(fecha_inicio, fecha_fin)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió un error al generar el Estado de Resultados: {e}"

@tool
def generar_balance_comprobacion_tool(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> str:
    """
    Genera un Balance de Comprobación de sumas y saldos. Es útil para verificar la
    igualdad de los débitos y créditos. Puede ser para un período específico o para
    todos los movimientos históricos si no se especifican fechas.
    Los parámetros 'fecha_inicio' y 'fecha_fin' deben estar en formato 'AAAA-MM-DD'.
    """
    try:
        resultado = reportes_logic.generar_balance_comprobacion(fecha_inicio, fecha_fin)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió un error al generar el Balance de Comprobación: {e}"

# Lista de todas las herramientas de contabilidad disponibles
contabilidad_tools = [
    generar_balance_general_tool,
    generar_estado_resultados_tool,
    generar_balance_comprobacion_tool,
]
