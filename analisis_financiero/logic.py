# analisis_financiero/logic.py
"""
Módulo para la lógica de negocio del Análisis Financiero.
Contiene las funciones para calcular los diferentes ratios.
"""
import logging
from typing import Dict, Any, Optional
from contabilidad import reportes_logic
import datetime
from langchain_core.tools import tool
import json

logger = logging.getLogger(__name__)

def _safe_div(numerador, denominador):
    """División segura para evitar errores de división por cero."""
    if denominador == 0:
        return 0.0
    return numerador / denominador

def calcular_ratios_liquidez(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los ratios de liquidez."""
    ac = datos.get('activo_corriente', 0.0)
    pc = datos.get('pasivo_corriente', 0.0)
    inventario = datos.get('inventario', 0.0)
    caja_bancos = datos.get('caja_y_bancos', 0.0)

    return {
        "ratio_liquidez_general": _safe_div(ac, pc),
        "prueba_acida": _safe_div((ac - inventario), pc),
        "prueba_defensiva": _safe_div(caja_bancos, pc),
        "capital_trabajo_neto": ac - pc
    }

def calcular_ratios_gestion(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los ratios de gestión o actividad."""
    cuentas_por_cobrar = datos.get('cuentas_por_cobrar', 0.0)
    ventas_credito = datos.get('ventas_a_credito', 0.0)
    inventario_promedio = datos.get('inventario_promedio', 0.0)
    costo_venta = datos.get('costo_de_venta', 0.0)
    ventas_totales = datos.get('ventas_totales', 0.0)
    activo_total = datos.get('activo_total', 0.0)

    return {
        "rotacion_cuentas_por_cobrar_dias": _safe_div(cuentas_por_cobrar * 365, ventas_credito),
        "rotacion_inventarios_dias": _safe_div(inventario_promedio * 365, costo_venta),
        "rotacion_activos_totales": _safe_div(ventas_totales, activo_total)
    }

def calcular_ratios_endeudamiento(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los ratios de endeudamiento."""
    pasivo_total = datos.get('pasivo_total', 0.0)
    activo_total = datos.get('activo_total', 0.0)
    patrimonio_neto = datos.get('patrimonio_neto', 0.0)
    uaii = datos.get('utilidad_antes_intereses_impuestos', 0.0)
    gastos_intereses = datos.get('gastos_intereses', 0.0)

    return {
        "endeudamiento_total": _safe_div(pasivo_total, activo_total),
        "razon_pasivo_patrimonio": _safe_div(pasivo_total, patrimonio_neto),
        "cobertura_intereses": _safe_div(uaii, gastos_intereses)
    }

def calcular_ratios_rentabilidad(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los ratios de rentabilidad."""
    utilidad_bruta = datos.get('utilidad_bruta', 0.0)
    ventas_totales = datos.get('ventas_totales', 0.0)
    utilidad_operacional = datos.get('utilidad_operacional', 0.0)
    utilidad_neta = datos.get('utilidad_neta', 0.0)
    activo_total = datos.get('activo_total', 0.0)
    patrimonio_neto = datos.get('patrimonio_neto', 0.0)

    return {
        "margen_utilidad_bruta": _safe_div(utilidad_bruta, ventas_totales),
        "margen_utilidad_operacional": _safe_div(utilidad_operacional, ventas_totales),
        "margen_utilidad_neta": _safe_div(utilidad_neta, ventas_totales),
        "retorno_sobre_activos_roa": _safe_div(utilidad_neta, activo_total),
        "retorno_sobre_patrimonio_roe": _safe_div(utilidad_neta, patrimonio_neto)
    }

def calcular_ratios_mercado(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los ratios de mercado y valoración."""
    utilidad_neta = datos.get('utilidad_neta', 0.0)
    acciones_circulacion = datos.get('acciones_en_circulacion', 0.0)
    precio_accion = datos.get('precio_por_accion', 0.0)
    valor_contable_por_accion = datos.get('valor_contable_por_accion', 0.0)
    capitalizacion_mercado = datos.get('capitalizacion_de_mercado', 0.0)
    ventas_anuales = datos.get('ventas_anuales', 0.0)
    dividendo_anual_accion = datos.get('dividendo_anual_por_accion', 0.0)

    bpa = _safe_div(utilidad_neta, acciones_circulacion)

    return {
        "beneficio_por_accion_bpa": bpa,
        "ratio_precio_beneficio_per": _safe_div(precio_accion, bpa),
        "ratio_precio_valor_contable_pvc": _safe_div(precio_accion, valor_contable_por_accion),
        "ratio_precio_ventas_psr": _safe_div(capitalizacion_mercado, ventas_anuales),
        "rentabilidad_por_dividendo": _safe_div(dividendo_anual_accion, precio_accion) * 100 if precio_accion > 0 else 0.0
    }

@tool
def generar_analisis_financiero_completo(fecha: str) -> str:
    """
    Orquesta la generación de todos los ratios financieros para una fecha específica.

    Args:
        fecha (str): La fecha de corte para el análisis, en formato 'AAAA-MM-DD'.

    Returns:
        str: Un string en formato JSON con todos los ratios calculados, agrupados por categoría.
    """
    logger.info(f"Iniciando análisis financiero completo para la fecha {fecha}")

    balance = reportes_logic.generar_balance_general(fecha)
    if not balance.get('total_activos'):
        return "Error: No se pudieron generar los datos del Balance General para la fecha dada. No hay datos para analizar."

    ano = datetime.datetime.strptime(fecha, '%Y-%m-%d').year
    fecha_inicio_ano = f"{ano}-01-01"
    estado_resultados = reportes_logic.generar_estado_resultados(fecha_inicio_ano, fecha)

    datos_consolidados = {
        "activo_corriente": balance.get('total_activos_corrientes', 0.0),
        "pasivo_corriente": balance.get('total_pasivos_corrientes', 0.0),
        "inventario": next((a['saldo_final'] for a in balance.get('activos', []) if a['codigo'].startswith('14')), 0.0),
        "caja_y_bancos": next((a['saldo_final'] for a in balance.get('activos', []) if a['codigo'].startswith('11')), 0.0),
        "cuentas_por_cobrar": next((a['saldo_final'] for a in balance.get('activos', []) if a['codigo'].startswith('13')), 0.0),
        "ventas_a_credito": estado_resultados.get('total_ingresos', 0.0),
        "costo_de_venta": estado_resultados.get('total_costos', 0.0),
        "ventas_totales": estado_resultados.get('total_ingresos', 0.0),
        "activo_total": balance.get('total_activos', 0.0),
        "pasivo_total": balance.get('total_pasivos', 0.0),
        "patrimonio_neto": balance.get('total_patrimonio', 0.0),
        "utilidad_bruta": estado_resultados.get('utilidad_bruta', 0.0),
        "utilidad_operacional": estado_resultados.get('utilidad_operacional', 0.0),
        "utilidad_neta": estado_resultados.get('utilidad_antes_impuestos', 0.0),
        "acciones_en_circulacion": 1000000, "precio_por_accion": 5.50,
    }
    datos_consolidados['valor_contable_por_accion'] = _safe_div(datos_consolidados['patrimonio_neto'], datos_consolidados['acciones_en_circulacion'])
    datos_consolidados['capitalizacion_de_mercado'] = datos_consolidados['precio_por_accion'] * datos_consolidados['acciones_en_circulacion']
    datos_consolidados['ventas_anuales'] = datos_consolidados['ventas_totales']

    analisis_final = {
        "Ratios de Liquidez": calcular_ratios_liquidez(datos_consolidados),
        "Ratios de Gestión": calcular_ratios_gestion(datos_consolidados),
        "Ratios de Endeudamiento": calcular_ratios_endeudamiento(datos_consolidados),
        "Ratios de Rentabilidad": calcular_ratios_rentabilidad(datos_consolidados),
        "Ratios de Mercado": calcular_ratios_mercado(datos_consolidados),
    }

    logger.info("Análisis financiero completado.")
    return json.dumps(analisis_final, indent=2, ensure_ascii=False)

@tool
def generar_historial_de_ratio(nombre_ratio: str, categoria_ratio: str, num_meses: int = 6) -> str:
    """
    Calcula el valor de un ratio financiero específico para los últimos N meses para ver su tendencia.

    Args:
        nombre_ratio (str): El nombre exacto del ratio a consultar (ej: 'prueba_acida').
        categoria_ratio (str): La categoría a la que pertenece el ratio (ej: 'Ratios de Liquidez').
        num_meses (int): El número de meses hacia atrás para generar el historial. Por defecto 6.

    Returns:
        str: Un string en formato JSON con las etiquetas (meses) y los valores del ratio.
    """
    logger.info(f"Generando historial para el ratio '{nombre_ratio}' en los últimos {num_meses} meses.")

    historial = {"labels": [], "values": []}
    today = datetime.date.today()

    for i in range(num_meses - 1, -1, -1):
        # Calcular el último día del mes para cada período anterior
        primer_dia_mes_actual = today.replace(day=1)
        mes_objetivo = primer_dia_mes_actual - datetime.timedelta(days=i * 30) # Aproximación
        ultimo_dia_mes_objetivo = (mes_objetivo.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)

        fecha_calculo = ultimo_dia_mes_objetivo.isoformat()

        try:
            analisis_mes = generar_analisis_financiero_completo(fecha_calculo)
            valor_ratio = analisis_mes[categoria_ratio][nombre_ratio]

            historial["labels"].append(ultimo_dia_mes_objetivo.strftime("%b %Y"))
            historial["values"].append(valor_ratio)
        except Exception as e:
            logger.error(f"No se pudo calcular el ratio para {fecha_calculo}: {e}")
            historial["labels"].append(ultimo_dia_mes_objetivo.strftime("%b %Y"))
            historial["values"].append(0) # Añadir 0 si hay un error

    return historial
