# activos_fijos/agents/tools/asset_tools.py
"""
Herramientas especializadas para que los agentes de activos fijos puedan interactuar
con la lógica de negocio del sistema.
"""
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from .... import logic as activos_fijos_logic

# --- Herramientas para el Capitán de Gestión de Activos ---

@tool
def registrar_nuevo_activo_tool(
    nombre: str, descripcion: str, fecha_adquisicion: str, costo_adquisicion: float,
    valor_residual: float, vida_util_meses: int, metodo_depreciacion: str,
    cuenta_activo: str, cuenta_dep_acum: str, cuenta_gasto_dep: str,
    cuenta_contrapartida: str
) -> str:
    """
    Registra un nuevo activo fijo en el sistema y contabiliza su adquisición.
    Debes proporcionar todos los detalles del activo y las cuentas contables relacionadas.
    El 'usuario_id' se obtiene de la sesión.
    """
    # Simulación del usuario_id, en un caso real vendría del contexto del agente.
    usuario_id_simulado = 1
    try:
        success = activos_fijos_logic.registrar_activo(
            nombre=nombre, descripcion=descripcion, fecha_adquisicion=fecha_adquisicion,
            costo_adquisicion=costo_adquisicion, valor_residual=valor_residual,
            vida_util_meses=vida_util_meses, metodo_depreciacion=metodo_depreciacion,
            cuenta_activo=cuenta_activo, cuenta_dep_acum=cuenta_dep_acum,
            cuenta_gasto_dep=cuenta_gasto_dep, usuario_id=usuario_id_simulado,
            cuenta_contrapartida=cuenta_contrapartida
        )
        if success:
            return f"Activo '{nombre}' registrado y contabilizado exitosamente."
        else:
            return "Fallo al registrar el activo. Verifique los logs para más detalles."
    except Exception as e:
        return f"Ocurrió una excepción inesperada: {e}"

@tool
def ejecutar_depreciacion_mensual_tool(ano: int, mes: int) -> str:
    """
    Ejecuta y contabiliza la depreciación de todos los activos para un mes y año específicos.
    """
    # Simulación del usuario_id
    usuario_id_simulado = 1
    try:
        success = activos_fijos_logic.ejecutar_proceso_depreciacion_mensual(
            ano=ano, mes=mes, usuario_id=usuario_id_simulado
        )
        if success:
            return f"Proceso de depreciación para {ano}-{mes} completado exitosamente."
        else:
            return f"Fallo en el proceso de depreciación para {ano}-{mes}."
    except Exception as e:
        return f"Ocurrió una excepción inesperada durante la depreciación: {e}"

# --- Herramientas para el Capitán de Reportería de Activos ---

@tool
def obtener_listado_activos_tool(estado: Optional[str] = None) -> str:
    """
    Obtiene un listado de todos los activos fijos en el sistema.
    Opcionalmente, puede filtrar por estado: "Activo" o "Dado de Baja".
    """
    try:
        activos = activos_fijos_logic.obtener_reporte_activos(estado=estado)
        if not activos:
            return "No se encontraron activos con los criterios especificados."
        # Serializar a JSON para una fácil lectura por el LLM
        return json.dumps(activos, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Ocurrió una excepción al obtener el reporte de activos: {e}"
