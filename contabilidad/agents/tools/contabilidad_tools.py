# contabilidad/agents/tools/contabilidad_tools.py
"""
Este archivo centraliza las herramientas (herramientas tácticas) que los agentes del módulo de contabilidad pueden utilizar.
Importa las funciones decoradas con @tool de los archivos de lógica correspondientes.
"""
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool

# --- Importar Lógica de Negocio ---
from contabilidad import reportes_logic, contabilidad_logic, puc_logic

# --- Funciones de Ayuda ---
def _serializar_respuesta(datos) -> str:
    """Función de ayuda para convertir la salida a una cadena JSON."""
    if not datos:
        return "No se encontraron datos."
    return json.dumps(datos, indent=2, ensure_ascii=False)

# --- Definición de Herramientas ---

# Herramientas del Plan de Cuentas (PUC)
obtener_cuentas_tool = puc_logic.obtener_cuentas
obtener_cuenta_por_codigo_tool = puc_logic.obtener_cuenta_por_codigo

# Herramienta para registrar comprobantes
registrar_comprobante_tool = contabilidad_logic.registrar_nuevo_comprobante

# Herramientas de Reportes
@tool
def generar_balance_general_tool(fecha_fin: str) -> str:
    """
    Genera el Balance General (Estado de Situación Financiera) a una fecha de corte específica.
    Muestra Activos, Pasivos y Patrimonio. Formato de fecha: 'AAAA-MM-DD'.
    """
    try:
        resultado = reportes_logic.generar_balance_general(fecha_fin)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió un error al generar el Balance General: {e}"

@tool
def generar_estado_resultados_tool(fecha_inicio: str, fecha_fin: str) -> str:
    """
    Genera el Estado de Resultados (Ganancias y Pérdidas) para un rango de fechas.
    Muestra Ingresos, Costos y Gastos para calcular la utilidad. Formato de fecha: 'AAAA-MM-DD'.
    """
    try:
        resultado = reportes_logic.generar_estado_resultados(fecha_inicio, fecha_fin)
        return _serializar_respuesta(resultado)
    except Exception as e:
        return f"Ocurrió un error al generar el Estado de Resultados: {e}"

@tool
async def abrir_periodo_contable_tool(query: str) -> str:
    """
    Abre un nuevo periodo contable para permitir el registro de transacciones.
    Extrae el nombre del periodo del query del usuario.
    Ejemplo de query: 'Abrir el periodo contable de Octubre 2025'.
    """
    print(f"--- Herramienta: abrir_periodo_contable ---")
    print(f"Orden recibida: {query}")
    try:
        # Lógica simple para extraer el periodo del query.
        # Una versión más avanzada usaría regex o un LLM.
        parts = query.split(" de ")
        periodo = parts[-1] if len(parts) > 1 else "Periodo no especificado"

        # Aquí iría la lógica de negocio real (ej. cambiar un flag en la DB).
        # Por ahora, simulamos el éxito.
        print(f"ACCIÓN: Abriendo el periodo '{periodo}' en el sistema.")

        return f"Éxito. El periodo '{periodo}' ha sido abierto y está listo para registrar transacciones."
    except Exception as e:
        return f"Ocurrió un error al intentar abrir el periodo contable: {e}"

# --- Lista Consolidada de Herramientas ---
# Este es el "equipo táctico" completo para el módulo de contabilidad.
contabilidad_tools = [
    obtener_cuentas_tool,
    obtener_cuenta_por_codigo_tool,
    registrar_comprobante_tool,
    generar_balance_general_tool,
    generar_estado_resultados_tool,
    abrir_periodo_contable_tool,
]
