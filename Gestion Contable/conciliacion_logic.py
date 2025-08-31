# logic/conciliacion_logic.py
"""
Módulo para la lógica de negocio de la Conciliación Bancaria.
"""
import logging
from typing import List, Dict, Any, Tuple
from database import db_manager

logger = logging.getLogger(__name__)

def obtener_datos_para_conciliacion(cuenta_banco_codigo: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Obtiene los datos necesarios para iniciar un proceso de conciliación.
    Devuelve una tupla con: (lista de transacciones bancarias, lista de movimientos contables).
    """
    transacciones = db_manager.obtener_transacciones_bancarias_no_reconciliadas()
    movimientos = db_manager.obtener_movimientos_contables_no_reconciliados(cuenta_banco_codigo)
    return transacciones, movimientos

def sugerir_coincidencias(transacciones: List[Dict[str, Any]], movimientos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compara las transacciones bancarias y los movimientos contables para sugerir coincidencias.
    Lógica inicial: buscar importes idénticos. El 'monto' de la transacción bancaria
    se compara con el 'debito' (salida de dinero) o 'credito' (entrada de dinero) del movimiento.
    """
    sugerencias = []
    # Usar copias para poder eliminar items ya emparejados
    movimientos_disponibles = list(movimientos)

    for trans in transacciones:
        monto_transaccion = trans['monto']

        for i, mov in enumerate(movimientos_disponibles):
            # Si el monto de la transacción es negativo (un pago), buscar en los débitos del banco.
            # Si el monto es positivo (un depósito), buscar en los créditos del banco.
            monto_movimiento = mov['debito'] if monto_transaccion < 0 else mov['credito']

            # Comparamos el valor absoluto
            if abs(abs(monto_transaccion) - monto_movimiento) < 0.01: # Tolerancia de 1 centavo
                sugerencias.append({
                    "transaccion": trans,
                    "movimiento": mov
                })
                # Eliminar el movimiento para que no se sugiera de nuevo
                movimientos_disponibles.pop(i)
                break # Pasar a la siguiente transacción bancaria

    logger.info(f"Se encontraron {len(sugerencias)} coincidencias sugeridas.")
    return sugerencias

def reconciliar_par(movimiento_id: int, transaccion_id: int) -> bool:
    """
    Ejecuta la reconciliación de un par de movimiento y transacción.
    """
    logger.info(f"Intentando reconciliar movimiento {movimiento_id} con transacción {transaccion_id}")
    return db_manager.marcar_como_reconciliados(movimiento_id, transaccion_id)

def importar_extracto_bancario(transacciones: List[Dict[str, Any]]) -> bool:
    """
    Procesa la importación de un extracto bancario.
    Aquí se podría añadir lógica de limpieza o transformación antes de insertar.
    """
    logger.info(f"Importando {len(transacciones)} transacciones del extracto.")
    return db_manager.insertar_transacciones_bancarias(transacciones)
