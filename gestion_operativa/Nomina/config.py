# -*- coding: utf-8 -*-
"""
Módulo de Configuración

Este archivo centraliza todas las constantes y valores legales para los cálculos de nómina en Colombia para el año 2024.
"""

# --- Valores Base 2024 ---
SALARIO_MINIMO_MENSUAL = 1300000.0
AUXILIO_DE_TRANSPORTE = 162000.0
UVT_2024 = 47065.0

# --- Parámetros Generales ---
# El auxilio de transporte se otorga a quienes ganan hasta 2 salarios mínimos
LIMITE_SUBSIDIO_TRANSPORTE_EN_SMMLV = 2.0

# La exoneración de aportes a salud y parafiscales aplica para salarios inferiores a 10 SMMLV
LIMITE_EXONERACION_APORTES_EN_SMMLV = 10.0

# --- Porcentajes de Aportes a Seguridad Social ---
# Contribuciones del Empleado
PORCENTAJE_SALUD_EMPLEADO = 0.04  # 4%
PORCENTAJE_PENSION_EMPLEADO = 0.04  # 4%

# Contribuciones del Empleador
PORCENTAJE_SALUD_EMPLEADOR = 0.085  # 8.5%
PORCENTAJE_PENSION_EMPLEADOR = 0.12   # 12%
# Nota: El riesgo profesional (ARL) varía por empresa/riesgo, se omite por ahora.

# --- Fondo de Solidaridad Pensional (FSP) ---
# Para salarios entre 4 y 16 SMMLV
PORCENTAJE_FSP_TRAMO_1 = 0.01  # 1%
LIMITE_INFERIOR_FSP_EN_SMMLV = 4.0
LIMITE_SUPERIOR_FSP_EN_SMMLV = 16.0
# Existen más tramos para salarios > 16 SMMLV, se pueden añadir después.

# --- Porcentajes de Aportes Parafiscales (Empleador) ---
PORCENTAJE_CAJA_COMPENSACION = 0.04  # 4%
PORCENTAJE_ICBF = 0.03  # 3%
PORCENTAJE_SENA = 0.02  # 2%

# --- Prestaciones Sociales ---
PORCENTAJE_CESANTIAS = 1 / 12  # Aproximadamente 8.33%
PORCENTAJE_INTERESES_CESANTIAS = 0.12  # 12% anual sobre las cesantías
PORCENTAJE_PRIMA = 1 / 12  # Aproximadamente 8.33% (un salario al año)
# Nota: Las vacaciones son 15 días de salario por año, no es un porcentaje directo sobre la nómina mensual.
# Fórmula Vacaciones: (Salario * DíasTrabajados) / 720
FACTOR_VACACIONES = 1 / 720.0
