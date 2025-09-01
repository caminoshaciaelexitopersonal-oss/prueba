# activos_fijos/logic.py
"""
Módulo para la lógica de negocio de la Gestión de Activos Fijos.
"""
import logging
import datetime
from typing import List, Dict, Any, Optional
from database import db_manager
from contabilidad import contabilidad_logic
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def registrar_activo(
    nombre: str, descripcion: str, fecha_adquisicion: str, costo_adquisicion: float,
    valor_residual: float, vida_util_meses: int, metodo_depreciacion: str,
    cuenta_activo: str, cuenta_dep_acum: str, cuenta_gasto_dep: str,
    cuenta_contrapartida: str, usuario_id: int = 1
) -> str:
    """
    Registra un nuevo activo fijo y su asiento contable de adquisición inicial.

    Args:
        nombre (str): Nombre descriptivo del activo (ej: 'Laptop Dell XPS 15').
        descripcion (str): Descripción más detallada del activo.
        fecha_adquisicion (str): Fecha de compra en formato 'AAAA-MM-DD'.
        costo_adquisicion (float): El costo total de compra del activo.
        valor_residual (float): El valor estimado del activo al final de su vida útil.
        vida_util_meses (int): La vida útil del activo en meses.
        metodo_depreciacion (str): Método de depreciación a usar. Actualmente soportado: 'linea_recta'.
        cuenta_activo (str): El código de la cuenta contable del activo (ej: '1528').
        cuenta_dep_acum (str): El código de la cuenta de depreciación acumulada (ej: '1592').
        cuenta_gasto_dep (str): El código de la cuenta para el gasto de depreciación (ej: '5160').
        cuenta_contrapartida (str): El código de la cuenta con la que se pagó o se generó la deuda (ej: '1110' para bancos, '2205' para proveedores).
        usuario_id (int): ID del usuario que registra. Por defecto es 1.

    Returns:
        str: Un mensaje de éxito o error.
    """
    success, activo_id = db_manager.crear_activo_fijo_db(
        nombre=nombre, descripcion=descripcion, fecha_adquisicion=fecha_adquisicion,
        costo_adquisicion=costo_adquisicion, valor_residual=valor_residual,
        vida_util_meses=vida_util_meses, metodo_depreciacion=metodo_depreciacion,
        cuenta_activo=cuenta_activo, cuenta_depreciacion_acumulada=cuenta_dep_acum,
        cuenta_gasto_depreciacion=cuenta_gasto_dep
    )
    if not success:
        return "Error: No se pudo crear el registro del activo fijo en la base de datos."

    descripcion_asiento = f"Compra de activo fijo: {nombre}"
    movimientos = [
        {"cuenta_codigo": cuenta_activo, "descripcion_detalle": descripcion_asiento, "debito": costo_adquisicion, "credito": 0},
        {"cuenta_codigo": cuenta_contrapartida, "descripcion_detalle": f"Pago/deuda por {nombre}", "debito": 0, "credito": costo_adquisicion},
    ]

    # La función de lógica contable ya es una herramienta y devuelve un string
    resultado_contable = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=fecha_adquisicion, tipo="Adquisición Activo",
        descripcion=descripcion_asiento, movimientos=movimientos, usuario_id=usuario_id
    )

    if "Error" in resultado_contable:
        logger.error(f"Se creó el activo ID {activo_id} pero falló su contabilización: {resultado_contable}")
        # En un sistema real, se debería implementar una lógica de rollback aquí.
        return f"Error: Se creó el activo pero falló la contabilización: {resultado_contable}"

    return f"Éxito: Activo '{nombre}' (ID: {activo_id}) y su asiento de adquisición han sido registrados. {resultado_contable}"

def _calcular_depreciacion_un_mes(activo: Dict[str, Any]) -> float:
    """
    Calcula la depreciación para un solo mes de un activo dado.
    Por ahora, solo implementa el método de línea recta.
    """
    if activo['metodo_depreciacion'].lower() == 'linea_recta':
        costo = activo['costo_adquisicion']
        residual = activo['valor_residual']
        vida_util = activo['vida_util_meses']
        if vida_util > 0:
            return (costo - residual) / vida_util
    return 0.0

@tool
def ejecutar_proceso_depreciacion_mensual(ano: int, mes: int, usuario_id: int = 1) -> str:
    """
    Ejecuta el proceso de depreciación para todos los activos para un mes y año dados y genera el comprobante contable correspondiente.

    Args:
        ano (int): El año para el cual ejecutar la depreciación (ej: 2023).
        mes (int): El mes para el cual ejecutar la depreciación (1-12).
        usuario_id (int): ID del usuario que ejecuta el proceso. Por defecto es 1.

    Returns:
        str: Un resumen del resultado del proceso.
    """
    activos = db_manager.obtener_activos_fijos_db(estado="Activo")
    if not activos:
        logger.info("No hay activos para depreciar.")
        return True

    fecha_proceso = f"{ano}-{mes:02d}-{datetime.date(ano, mes, 1).max.day}"
    resumen_depreciacion = {} # { (gasto_cta, dep_acum_cta): total_monto }

    for activo in activos:
        # Simple validación para no depreciar más allá de la vida útil
        # Una lógica más compleja consideraría la depreciación acumulada hasta la fecha.
        depreciacion_mes = _calcular_depreciacion_un_mes(activo)
        if depreciacion_mes > 0:
            llave = (activo['cuenta_gasto_depreciacion'], activo['cuenta_depreciacion_acumulada'])
            resumen_depreciacion[llave] = resumen_depreciacion.get(llave, 0) + depreciacion_mes

    if not resumen_depreciacion:
        logger.info("No se calculó depreciación para ningún activo este mes.")
        return True

    # Construir los movimientos para el comprobante contable
    movimientos = []
    total_depreciacion_mes = 0
    for (gasto_cta, dep_acum_cta), monto in resumen_depreciacion.items():
        movimientos.append({"cuenta_codigo": gasto_cta, "descripcion_detalle": "Depreciación del mes", "debito": monto, "credito": 0})
        movimientos.append({"cuenta_codigo": dep_acum_cta, "descripcion_detalle": "Depreciación del mes", "debito": 0, "credito": monto})
        total_depreciacion_mes += monto

    descripcion_asiento = f"Depreciación para el período {ano}-{mes:02d}"

    success, _ = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=fecha_proceso, tipo="Depreciación",
        descripcion=descripcion_asiento, movimientos=movimientos, usuario_id=usuario_id
    )

    if success:
        logger.info(f"Comprobante de depreciación generado exitosamente por un total de {total_depreciacion_mes:.2f}")
    else:
        logger.error("Fallo al generar el comprobante de depreciación del mes.")

    return success
