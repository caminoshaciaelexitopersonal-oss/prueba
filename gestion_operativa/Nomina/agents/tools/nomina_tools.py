# gestion_operativa/Nomina/agents/tools/nomina_tools.py

"""
Este archivo centraliza las herramientas tácticas que los agentes del módulo de Nómina pueden utilizar.
"""

# Importar herramientas de gestión de empleados
from gestion_operativa.Nomina.tools.employee_tools import (
    add_employee,
    list_employees,
)

# Importar herramientas de cálculo de nómina
from gestion_operativa.Nomina.tools.payroll_tools import (
    calculate_social_security,
    calculate_parafiscals,
    calculate_social_benefits,
    calculate_withholding_tax,
)

# Lista consolidada de todas las herramientas disponibles
nomina_tools = [
    add_employee,
    list_employees,
    calculate_social_security,
    calculate_parafiscals,
    calculate_social_benefits,
    calculate_withholding_tax,
]
