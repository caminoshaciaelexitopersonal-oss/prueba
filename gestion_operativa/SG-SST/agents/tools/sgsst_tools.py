# gestion_operativa/SG-SST/agents/tools/sgsst_tools.py

"""
Este archivo centraliza todas las herramientas tácticas que los agentes del módulo de SG-SST pueden utilizar.
"""

# Herramientas existentes
from gestion_operativa.SG_SST.tools.incident_tools import report_incident, list_incidents
from gestion_operativa.SG_SST.tools.risk_tools import add_risk, list_risks

# Nuevas herramientas creadas
from gestion_operativa.SG_SST.tools.plan_tools import create_annual_sgsst_plan, add_activity_to_annual_plan
from gestion_operativa.SG_SST.tools.document_tools import create_sgsst_document, find_sgsst_document
from gestion_operativa.SG_SST.tools.training_tools import record_sgsst_training, record_ppe_delivery
from gestion_operativa.SG_SST.tools.indicator_tools import define_sgsst_indicator, list_sgsst_indicators

# Lista consolidada de todas las herramientas disponibles para el "Ejército de SG-SST"
sgsst_tools = [
    # Herramientas de Incidentes
    report_incident,
    list_incidents,
    # Herramientas de Riesgos
    add_risk,
    list_risks,
    # Herramientas de Planificación
    create_annual_sgsst_plan,
    add_activity_to_annual_plan,
    # Herramientas de Documentación
    create_sgsst_document,
    find_sgsst_document,
    # Herramientas de Capacitación
    record_sgsst_training,
    record_ppe_delivery,
    # Herramientas de Indicadores
    define_sgsst_indicator,
    list_sgsst_indicators,
]
