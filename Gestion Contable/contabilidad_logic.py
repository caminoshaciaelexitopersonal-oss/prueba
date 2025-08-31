# logic/contabilidad_logic.py
import logging

logger = logging.getLogger(__name__)

def validar_partida_doble(movimientos: list[dict]) -> bool:
    """
    Valida que la suma de débitos sea igual a la suma de créditos.
    Espera una lista de diccionarios, cada uno con 'debito' y 'credito'.
    """
    total_debito = sum(float(m.get('debito', 0) or 0) for m in movimientos)
    total_credito = sum(float(m.get('credito', 0) or 0) for m in movimientos)

    logger.info(f"Validación partida doble: Débitos={total_debito}, Créditos={total_credito}")

    # Usar una pequeña tolerancia para comparar floats
    return abs(total_debito - total_credito) < 0.01 # Tolerancia de 1 centavo

# --- Lógica de Impuestos ---

def calcular_iva(base: float, tarifa: float) -> float:
    """
    Calcula el valor del IVA.
    Aplica la tarifa directamente sobre la base.
    """
    if base < 0 or tarifa < 0:
        logger.error("La base y la tarifa del IVA no pueden ser negativas.")
        return 0.0

    logger.info(f"Calculando IVA: base={base}, tarifa={tarifa}%")
    return base * (tarifa / 100)

def calcular_retencion_fuente(base: float, concepto: str, es_autoretenedor: bool = False) -> float:
    """
    Calcula la retención en la fuente basado en un concepto y una base.

    Esta es una implementación simplificada. Una versión completa requeriría
    una base de datos de conceptos, tarifas, y reglas fiscales complejas.
    """
    if es_autoretenedor:
        logger.info("El declarante es autorretenedor, no se aplica retención en la fuente por terceros.")
        return 0.0

    # Tabla simplificada de conceptos de retención. A futuro, esto estaría en la BD.
    # Las bases están en UVT (Unidad de Valor Tributario).
    TABLA_RETENCIONES = {
        "servicios_generales": {"base_uvt": 4, "tarifa": 0.06},
        "compras_generales": {"base_uvt": 27, "tarifa": 0.025},
        "honorarios": {"base_uvt": 0, "tarifa": 0.11},
        "arrendamientos_bienes_muebles": {"base_uvt": 0, "tarifa": 0.04},
    }

    # El valor de la UVT debe ser configurable o actualizado anualmente.
    VALOR_UVT_ANUAL = 47065 # Valor de la UVT para 2024 a modo de ejemplo.

    if concepto not in TABLA_RETENCIONES:
        logger.warning(f"Concepto de retención '{concepto}' no encontrado en la tabla simplificada.")
        return 0.0

    regla = TABLA_RETENCIONES[concepto]
    base_minima_en_pesos = regla["base_uvt"] * VALOR_UVT_ANUAL

    if regla["base_uvt"] > 0 and base < base_minima_en_pesos:
        logger.info(f"La base ({base}) no supera la base mínima de {base_minima_en_pesos} para '{concepto}'. No se aplica retención.")
        return 0.0

    retencion = base * regla["tarifa"]
    logger.info(f"Cálculo de Retefuente para '{concepto}': base={base}, tarifa={regla['tarifa']*100}%, resultado={retencion}")
    return retencion

from typing import List, Dict, Any, Optional, Tuple
from database import db_manager

def registrar_nuevo_comprobante(fecha: str, tipo: str, descripcion: str, movimientos: List[Dict[str, Any]], usuario_id: int) -> Tuple[bool, Optional[int]]:
    """
    Realiza las validaciones de negocio y registra un nuevo comprobante.
    Devuelve (True, comprobante_id) si es exitoso, (False, None) en caso contrario.
    """
    # 1. Validar partida doble
    if not validar_partida_doble(movimientos):
        logger.error("Error de validación: La partida doble no cuadra.")
        return False, None

    # 2. Aquí podrían ir otras validaciones de negocio (ej: cuentas que no existen, etc.)
    # La validación de existencia de cuenta ya se hace en la transacción de db_manager, lo cual es bueno.

    # 3. Llamar al gestor de base de datos para guardar
    return db_manager.agregar_comprobante_y_movimientos(
        fecha=fecha,
        tipo=tipo,
        descripcion=descripcion,
        movimientos=movimientos,
        usuario_id=usuario_id
    )

def obtener_lista_comprobantes(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de comprobantes recientes.
    """
    return db_manager.obtener_comprobantes(limit=limit)

def obtener_detalle_comprobante(comprobante_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene los movimientos (detalles) de un comprobante específico.
    """
    return db_manager.obtener_movimientos_por_comprobante(comprobante_id)


# Más funciones de lógica contable irán aquí (ej: generar estados financieros)