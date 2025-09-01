# agents/tools/contabilidad_tools.py
"""
Herramientas especializadas para que el agente de contabilidad pueda interactuar
con la lógica de negocio y la base de datos del sistema contable.
"""
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from contabilidad import reportes_logic, contabilidad_logic

def _serializar_respuesta(datos) -> str:
    """Función de ayuda para convertir la salida a una cadena JSON."""
    if not datos:
        return "No se encontraron datos."
    # Convertir a JSON string. El LLM puede procesar esto fácilmente.
    return json.dumps(datos, indent=2, ensure_ascii=False)

@tool
def crear_asiento_contable_tool(descripcion: str, movimientos: List[Dict[str, Any]], fecha: Optional[str] = None) -> str:
    """
    Crea un nuevo asiento o comprobante contable en el sistema.
    Esta herramienta es para registrar transacciones como compras, ventas, pagos, etc.
    Debes proporcionar una descripción clara de la transacción y una lista de los movimientos de la partida doble.
    El parámetro 'movimientos' debe ser una lista de diccionarios, donde cada diccionario representa una línea y debe contener:
    - 'cuenta_codigo': El código de la cuenta contable (ej: '110505' para Caja General).
    - 'debito': El valor del débito. Poner 0 si es un crédito.
    - 'credito': El valor del crédito. Poner 0 si es un débito.
    La suma de todos los débitos debe ser igual a la suma de todos los créditos.
    El parámetro 'fecha' es opcional, si no se provee se usará la fecha actual. Formato: 'AAAA-MM-DD'.
    El 'usuario_id' se obtiene automáticamente de la sesión del usuario.
    """
    # NOTA: En un sistema real, el usuario_id debería obtenerse del contexto de la sesión del agente,
    # no hardcodearse. Para este ejemplo, se simula.
    usuario_id_simulado = 1

    try:
        # Validar que los movimientos no estén vacíos
        if not movimientos or not isinstance(movimientos, list) or len(movimientos) < 2:
            return "Error de validación: Se requieren al menos dos movimientos para la partida doble."

        success, result = contabilidad_logic.registrar_asiento_desde_agente(
            descripcion=descripcion,
            movimientos=movimientos,
            usuario_id=usuario_id_simulado,
            fecha=fecha
        )
        if success:
            return f"Asiento contable creado exitosamente con el ID: {result}."
        else:
            # El resultado 'result' puede contener el mensaje de error de la lógica
            return f"Error al crear el asiento contable: {result}"
    except Exception as e:
        return f"Ocurrió una excepción inesperada al crear el asiento contable: {e}"

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
    crear_asiento_contable_tool,
    generar_balance_general_tool,
    generar_estado_resultados_tool,
    generar_balance_comprobacion_tool,
]
