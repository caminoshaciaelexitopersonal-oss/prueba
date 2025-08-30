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

# --- Placeholder para futuras lógicas ---

def calcular_iva(base: float, tarifa: float) -> float:
    """Calcula el valor del IVA (placeholder)."""
    # Aquí iría la lógica real según tipo de bien/servicio y régimen
    return base * (tarifa / 100)

def calcular_retencion_fuente(base: float, concepto: str, regimen_declarante: str, regimen_retenido: str) -> float:
    """Calcula la retención en la fuente (placeholder)."""
    # Lógica muy compleja que depende de bases, tarifas, conceptos, tipos de contribuyente, etc.
    logger.warning("Cálculo de Retención en la Fuente no implementado detalladamente.")
    return 0.0 # Devuelve 0 como placeholder

# Más funciones de lógica contable irán aquí (ej: generar estados financieros)