# -*- coding: utf-8 -*-
from langchain_core.tools import tool
import config

@tool
def calculate_social_security(salary: float) -> dict:
    """
    Calculates the social security contributions (Health and Pension)
    for a given monthly salary based on Colombian law for 2024.

    Args:
        salary: The monthly salary of the employee.

    Returns:
        A dictionary with a detailed breakdown of the contributions.
    """

    ibc = salary  # Ingreso Base de Cotización
    # Add transportation allowance to IBC if applicable
    if salary <= (config.SALARIO_MINIMO_MENSUAL * config.LIMITE_SUBSIDIO_TRANSPORTE_EN_SMMLV):
        ibc += config.AUXILIO_DE_TRANSPORTE

    # Employee contributions
    health_employee = ibc * config.PORCENTAJE_SALUD_EMPLEADO
    pension_employee = ibc * config.PORCENTAJE_PENSION_EMPLEADO

    # Employer contributions
    pension_employer = ibc * config.PORCENTAJE_PENSION_EMPLEADOR

    # Check for exemption on employer's health contribution
    if salary < (config.SALARIO_MINIMO_MENSUAL * config.LIMITE_EXONERACION_APORTES_EN_SMMLV):
        health_employer = 0
        exemption_applied = True
    else:
        health_employer = ibc * config.PORCENTAJE_SALUD_EMPLEADOR
        exemption_applied = False

    # FSP contribution
    fsp_contribution = 0.0
    if config.LIMITE_INFERIOR_FSP_EN_SMMLV <= (salary / config.SALARIO_MINIMO_MENSUAL) < config.LIMITE_SUPERIOR_FSP_EN_SMMLV:
        fsp_contribution = ibc * config.PORCENTAJE_FSP_TRAMO_1

    total_employee_deductions = health_employee + pension_employee + fsp_contribution
    total_employer_cost = health_employer + pension_employer

    return {
        "base_income_ibc": ibc,
        "employee_deductions": {
            "health": health_employee,
            "pension": pension_employee,
            "fsp": fsp_contribution,
            "total": total_employee_deductions,
        },
        "employer_contributions": {
            "health": health_employer,
            "pension": pension_employer,
            "total": total_employer_cost,
            "exemption_applied": exemption_applied,
        },
        "net_salary_before_benefits": salary - total_employee_deductions
    }

@tool
def calculate_parafiscals(salary: float) -> dict:
    """
    Calculates the parafiscal contributions (SENA, ICBF, Caja de Compensación)
    for a given monthly salary based on Colombian law for 2024.

    Args:
        salary: The monthly salary of the employee.

    Returns:
        A dictionary with a detailed breakdown of the contributions.
    """

    # Check for exemption on SENA and ICBF contributions
    if salary < (config.SALARIO_MINIMO_MENSUAL * config.LIMITE_EXONERACION_APORTES_EN_SMMLV):
        sena_contribution = 0
        icbf_contribution = 0
        exemption_applied = True
    else:
        sena_contribution = salary * config.PORCENTAJE_SENA
        icbf_contribution = salary * config.PORCENTAJE_ICBF
        exemption_applied = False

    # Caja de Compensación is never exempt
    caja_contribution = salary * config.PORCENTAJE_CAJA_COMPENSACION

    total_parafiscals = sena_contribution + icbf_contribution + caja_contribution

    return {
        "sena": sena_contribution,
        "icbf": icbf_contribution,
        "caja_compensacion": caja_contribution,
        "total": total_parafiscals,
        "exemption_applied": exemption_applied,
    }

@tool
def calculate_social_benefits(salary: float, days_worked_year: int, days_worked_semester: int) -> dict:
    """
    Calculates the social benefits (Cesantías, Intereses, Prima)
    for a given salary and time worked.

    Args:
        salary: The monthly salary of the employee.
        days_worked_year: The total number of days worked in the year for Cesantías.
        days_worked_semester: The total number of days worked in the semester for Prima.

    Returns:
        A dictionary with the calculated social benefits.
    """
    base_salary = salary
    # The base for these calculations includes transportation allowance
    if salary <= (config.SALARIO_MINIMO_MENSUAL * config.LIMITE_SUBSIDIO_TRANSPORTE_EN_SMMLV):
        base_salary += config.AUXILIO_DE_TRANSPORTE

    # Cesantías (Severance Pay)
    cesantias = (base_salary * days_worked_year) / 360

    # Intereses sobre Cesantías (Interest on Severance)
    intereses_cesantias = (cesantias * days_worked_year * 0.12) / 360

    # Prima de Servicios (Service Bonus)
    prima = (base_salary * days_worked_semester) / 360

    return {
        "cesantias": cesantias,
        "intereses_sobre_cesantias": intereses_cesantias,
        "prima_de_servicios": prima,
        "total_benefits": cesantias + intereses_cesantias + prima
    }

@tool
def calculate_withholding_tax(salary: float) -> dict:
    """
    Calculates the withholding tax ("Retención en la Fuente") for a given
    monthly salary based on Colombian law for 2024.
    This uses the simplified procedure for asalariados (Art. 383 E.T.).
    Does not include complex deductions like dependents, prepaid medicine, etc.

    Args:
        salary: The monthly salary of the employee.

    Returns:
        A dictionary with the withholding tax calculation.
    """
    # 1. Determine the taxable income base
    # Start with the salary
    taxable_base = salary

    # Subtract non-taxable income (social security contributions)
    # Note: A full implementation would consider more deductions.
    social_security = calculate_social_security(salary)
    taxable_base -= social_security['employee_deductions']['total']

    # 2. Convert the taxable base to UVT
    uvt_value = config.UVT_2024  # Let's add UVT to config
    base_in_uvt = taxable_base / uvt_value

    # 3. Apply the progressive tax table (Art. 383 E.T. adapted)
    tax_in_uvt = 0.0
    if 95 < base_in_uvt <= 150:
        tax_in_uvt = (base_in_uvt - 95) * 0.19
    elif 150 < base_in_uvt <= 360:
        tax_in_uvt = (base_in_uvt - 150) * 0.28 + 10
    elif 360 < base_in_uvt <= 640:
        tax_in_uvt = (base_in_uvt - 360) * 0.33 + 60
    elif 640 < base_in_uvt <= 945:
        tax_in_uvt = (base_in_uvt - 640) * 0.35 + 135
    elif 945 < base_in_uvt <= 2300:
        tax_in_uvt = (base_in_uvt - 945) * 0.37 + 275
    elif base_in_uvt > 2300:
        tax_in_uvt = (base_in_uvt - 2300) * 0.39 + 780

    # 4. Convert the tax from UVT back to pesos
    tax_in_pesos = tax_in_uvt * uvt_value

    return {
        "taxable_base_pesos": taxable_base,
        "taxable_base_uvt": base_in_uvt,
        "tax_in_uvt": tax_in_uvt,
        "withholding_tax_pesos": tax_in_pesos,
    }
