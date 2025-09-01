# gestion_operativa/SG-SST/agents/tools/sgsst_tools.py

"""
Este archivo centraliza las herramientas tácticas que los agentes del módulo de SG-SST pueden utilizar.
"""

# Importar herramientas de gestión de incidentes
from gestion_operativa.SG_SST.tools.incident_tools import (
    report_incident,
    list_incidents,
)

# Importar herramientas de gestión de riesgos
from gestion_operativa.SG_SST.tools.risk_tools import (
    add_risk,
    list_risks,
)

# Lista consolidada de todas las herramientas disponibles
sgsst_tools = [
    report_incident,
    list_incidents,
    add_risk,
    list_risks,
]
