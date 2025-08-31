# logic/reportes_logic.py
"""
Módulo para la lógica de negocio de la generación de informes financieros.
"""
import logging
import datetime
from typing import List, Dict, Any, Optional
from database import db_manager

logger = logging.getLogger(__name__)

def generar_balance_comprobacion(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Genera un balance de comprobación de saldos para un rango de fechas.

    1. Obtiene todas las cuentas del plan.
    2. Obtiene todos los movimientos del libro diario en el rango de fechas.
    3. Calcula el saldo final para cada cuenta basado en su naturaleza.
    4. Devuelve una lista de diccionarios, cada uno representando una cuenta con su saldo.
    """
    logger.info(f"Generando Balance de Comprobación desde {fecha_inicio} hasta {fecha_fin}")

    # 1. Obtener todas las cuentas
    plan_cuentas = db_manager.obtener_cuentas_puc()
    if not plan_cuentas:
        logger.warning("No hay cuentas en el plan para generar el balance.")
        return []

    # Crear un diccionario para almacenar los saldos de cada cuenta
    saldos = {cuenta['codigo']: {'debito': 0.0, 'credito': 0.0, **cuenta} for cuenta in plan_cuentas}

    # 2. Obtener todos los movimientos relevantes
    movimientos = db_manager.obtener_libro_diario(fecha_inicio, fecha_fin)
    logger.info(f"Procesando {len(movimientos)} movimientos.")

    # 3. Calcular los totales de débito y crédito para cada cuenta
    for mov in movimientos:
        codigo = mov['cuenta_codigo']
        if codigo in saldos:
            saldos[codigo]['debito'] += mov.get('debito', 0.0)
            saldos[codigo]['credito'] += mov.get('credito', 0.0)

    # 4. Calcular el saldo final y formatear la salida
    balance_final = []
    for codigo, data in saldos.items():
        debito_total = data['debito']
        credito_total = data['credito']
        naturaleza = data['naturaleza']
        saldo = 0.0

        if naturaleza == 'Debito':
            saldo = debito_total - credito_total
        else: # Naturaleza es 'Credito'
            saldo = credito_total - debito_total

        # Solo agregar al reporte si hubo movimientos o si queremos mostrar todas las cuentas
        if debito_total > 0 or credito_total > 0:
            balance_final.append({
                'codigo': codigo,
                'nombre': data['nombre'],
                'naturaleza': naturaleza,
                'total_debito': debito_total,
                'total_credito': credito_total,
                'saldo_final': saldo
            })

    logger.info(f"Balance de Comprobación generado con {len(balance_final)} cuentas con movimiento.")
    return sorted(balance_final, key=lambda x: x['codigo'])

def generar_estado_resultados(fecha_inicio: str, fecha_fin: str) -> Dict[str, Any]:
    """
    Genera un Estado de Resultados (Ingresos vs Gastos) para un período.
    """
    logger.info(f"Generando Estado de Resultados desde {fecha_inicio} hasta {fecha_fin}")
    balance = generar_balance_comprobacion(fecha_inicio, fecha_fin)

    ingresos = []
    gastos = []
    costos = []

    total_ingresos = 0.0
    total_gastos = 0.0
    total_costos = 0.0

    for cuenta in balance:
        codigo = cuenta['codigo']
        saldo = cuenta['saldo_final']

        if codigo.startswith('4'): # Ingresos
            ingresos.append(cuenta)
            total_ingresos += saldo
        elif codigo.startswith('5'): # Gastos
            gastos.append(cuenta)
            total_gastos += saldo
        elif codigo.startswith('6') or codigo.startswith('7'): # Costos
            costos.append(cuenta)
            total_costos += saldo

    utilidad_bruta = total_ingresos - total_costos
    utilidad_operacional = utilidad_bruta - total_gastos
    # Simplificado: no se manejan impuestos ni utilidad neta por ahora
    utilidad_antes_impuestos = utilidad_operacional

    return {
        "ingresos": ingresos,
        "total_ingresos": total_ingresos,
        "costos": costos,
        "total_costos": total_costos,
        "gastos": gastos,
        "total_gastos": total_gastos,
        "utilidad_bruta": utilidad_bruta,
        "utilidad_operacional": utilidad_operacional,
        "utilidad_antes_impuestos": utilidad_antes_impuestos
    }

def generar_balance_general(fecha_fin: str) -> Dict[str, Any]:
    """
    Genera un Balance General (Activos, Pasivos, Patrimonio) a una fecha de corte.
    """
    logger.info(f"Generando Balance General a fecha {fecha_fin}")
    # El balance debe ser desde el inicio de los tiempos hasta la fecha de corte
    balance_historico = generar_balance_comprobacion(None, fecha_fin)

    activos = []
    pasivos = []
    patrimonio = []

    total_activos = 0.0
    total_pasivos = 0.0
    total_patrimonio_inicial = 0.0

    # Calcular resultado del ejercicio actual para añadirlo al patrimonio
    # Asumimos que el ejercicio contable es el año de la fecha de fin
    inicio_ejercicio = f"{datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').year}-01-01"
    resultado_ejercicio = generar_estado_resultados(inicio_ejercicio, fecha_fin)['utilidad_antes_impuestos']

    for cuenta in balance_historico:
        codigo = cuenta['codigo']
        saldo = cuenta['saldo_final']

        if codigo.startswith('1'): # Activos
            activos.append(cuenta)
            total_activos += saldo
        elif codigo.startswith('2'): # Pasivos
            pasivos.append(cuenta)
            total_pasivos += saldo
        elif codigo.startswith('3'): # Patrimonio
            patrimonio.append(cuenta)
            total_patrimonio_inicial += saldo

    total_patrimonio = total_patrimonio_inicial + resultado_ejercicio

    # Ecuación contable: Activo = Pasivo + Patrimonio
    ecuacion_check = total_activos - (total_pasivos + total_patrimonio)

    return {
        "activos": activos,
        "total_activos": total_activos,
        "pasivos": pasivos,
        "total_pasivos": total_pasivos,
        "patrimonio": patrimonio,
        "total_patrimonio_inicial": total_patrimonio_inicial,
        "resultado_del_ejercicio": resultado_ejercicio,
        "total_patrimonio": total_patrimonio,
        "verificacion_ecuacion": ecuacion_check
    }
