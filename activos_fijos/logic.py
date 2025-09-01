# activos_fijos/logic.py
"""
Módulo para la lógica de negocio de la Gestión de Activos Fijos.
"""
import logging
import datetime
from typing import List, Dict, Any, Optional
from database import db_manager
from contabilidad import contabilidad_logic

logger = logging.getLogger(__name__)

def registrar_activo(
    nombre: str, descripcion: str, fecha_adquisicion: str, costo_adquisicion: float,
    valor_residual: float, vida_util_meses: int, metodo_depreciacion: str,
    cuenta_activo: str, cuenta_dep_acum: str, cuenta_gasto_dep: str,
    usuario_id: int, cuenta_contrapartida: str # Ej: 1110 (Bancos) o 2205 (Proveedores)
) -> bool:
    """
    Registra un nuevo activo fijo y su asiento contable de adquisición.
    """
    # 1. Guardar el activo en la base de datos
    success, activo_id = db_manager.crear_activo_fijo_db(
        nombre=nombre, descripcion=descripcion, fecha_adquisicion=fecha_adquisicion,
        costo_adquisicion=costo_adquisicion, valor_residual=valor_residual,
        vida_util_meses=vida_util_meses, metodo_depreciacion=metodo_depreciacion,
        cuenta_activo=cuenta_activo, cuenta_depreciacion_acumulada=cuenta_dep_acum,
        cuenta_gasto_depreciacion=cuenta_gasto_dep
    )
    if not success:
        return False

    # 2. Generar el asiento contable de la adquisición
    descripcion_asiento = f"Compra de activo fijo: {nombre}"
    movimientos = [
        {"cuenta_codigo": cuenta_activo, "descripcion_detalle": descripcion_asiento, "debito": costo_adquisicion, "credito": 0},
        {"cuenta_codigo": cuenta_contrapartida, "descripcion_detalle": f"Pago/deuda por {nombre}", "debito": 0, "credito": costo_adquisicion},
    ]

    success_contable, _ = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=fecha_adquisicion, tipo="Adquisición Activo",
        descripcion=descripcion_asiento, movimientos=movimientos, usuario_id=usuario_id
    )

    if not success_contable:
        # En un sistema real, se debería manejar este error (ej: borrar el activo creado)
        logger.error(f"Se creó el activo ID {activo_id} pero falló su contabilización.")
        return False

    return True

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

def ejecutar_proceso_depreciacion_mensual(ano: int, mes: int, usuario_id: int) -> bool:
    """
    Ejecuta el proceso de depreciación para todos los activos para un mes y año dados.
    Genera un único comprobante contable con el resumen de la depreciación del mes.
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

def obtener_reporte_activos(estado: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Obtiene una lista de activos fijos, opcionalmente filtrados por estado (ej: "Activo", "Dado de Baja").
    """
    logger.info(f"Obteniendo reporte de activos con estado: {estado if estado else 'Todos'}")
    return db_manager.obtener_activos_fijos_db(estado=estado)
