import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal

from .general import AgentState

# Definición de los 15 capitanes y sus responsabilidades
CAPTAIN_INFO = [
    {"name": "matriz_peligros", "description": "Gestiona la identificación, valoración y control de riesgos y peligros (IPERC). Ideal para tareas sobre crear, actualizar o consultar la matriz de riesgos."},
    {"name": "inspecciones_seguridad", "description": "Ejecuta inspecciones planeadas de áreas, equipos, herramientas y EPP. Ideal para órdenes sobre programar, realizar o consultar inspecciones de seguridad."},
    {"name": "evaluaciones_ocupacionales", "description": "Gestiona evaluaciones ergonómicas, psicosociales y mediciones de higiene (ruido, iluminación). Ideal para solicitudes de evaluaciones de puestos de trabajo o mediciones ambientales."},
    {"name": "planes_procedimientos", "description": "Elabora planes de trabajo, procedimientos de tareas críticas (PETS) y permisos de trabajo de alto riesgo (PTAR). Ideal para crear o modificar procedimientos y planes de seguridad."},
    {"name": "gestion_documental", "description": "Controla y versiona todos los documentos del sistema: políticas, manuales, formatos y registros. Ideal para tareas de archivar, buscar o actualizar documentos oficiales de SST."},
    {"name": "cumplimiento_normatividad", "description": "Mantiene la biblioteca de leyes y normas, y ejecuta auditorías internas. Ideal para consultas sobre la normativa legal vigente o para programar auditorías."},
    {"name": "capacitacion_competencias", "description": "Gestiona la matriz de capacitación, inducciones y entrenamientos. Ideal para registrar, programar o verificar la formación del personal en SST."},
    {"name": "cultura_participacion", "description": "Administra el COPASST, comités, campañas de seguridad y programas de liderazgo. Ideal para tareas relacionadas con el comité paritario o la organización de campañas."},
    {"name": "bienestar_laboral", "description": "Desarrolla programas de salud mental, pausas activas y prevención del acoso. Ideal para iniciativas de bienestar para los empleados."},
    {"name": "investigacion_accidentes", "description": "Registra e investiga incidentes, accidentes y enfermedades laborales. Ideal para reportar un accidente o consultar el estado de una investigación."},
    {"name": "preparacion_emergencias", "description": "Gestiona planes de emergencia, brigadas y simulacros. Ideal para todo lo relacionado con la preparación y respuesta ante emergencias."},
    {"name": "salud_ocupacional", "description": "Realiza seguimiento a exámenes médicos y programas de vigilancia epidemiológica (PVE). Ideal para gestionar citas de exámenes médicos o consultar PVEs."},
    {"name": "gestion_contratistas", "description": "Controla y sigue la seguridad y salud de trabajadores de empresas terceras. Ideal para verificar el cumplimiento de SST de un contratista."},
    {"name": "indicadores_analitica", "description": "Mide, sigue y reporta los indicadores clave de desempeño (KPIs) del sistema. Ideal para generar reportes o dashboards de estadísticas de SST."},
    {"name": "innovacion_tecnologia", "description": "Implementa nuevas tecnologías (apps, IoT, VR) para la gestión de SST. Ideal para proyectos de innovación tecnológica en seguridad."},
]

def route_to_captain(state: AgentState):
    command = state.get("command", "").lower()

    if os.getenv("ROUTER_DEBUG_MODE") == "true":
        print("---ROUTER DE CAPITANES (Modo Debug por Palabras Clave)---")
        if "inspección" in command or "inspeccionar" in command:
            captain_name = "inspecciones_seguridad"
        elif "peligro" in command or "iperc" in command or "matriz" in command:
            captain_name = "matriz_peligros"
        elif "procedimiento" in command or "pet" in command or "ptar" in command:
            captain_name = "planes_procedimientos"
        else:
            captain_name = "fallback"
        print(f"Comando: '{command}'")
        print(f"Enrutado por palabra clave a: {captain_name}")
        return {"captain": captain_name}

    print("---ROUTER INTELIGENTE DE CAPITANES (SG-SST)---")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    captain_names = [c['name'] for c in CAPTAIN_INFO] + ["fallback"]
    CaptainName = Literal[tuple(captain_names)]
    class CaptainRouter(BaseModel):
        captain: CaptainName = Field(description="El nombre del capitán más adecuado.")
    parser = JsonOutputParser(pydantic_object=CaptainRouter)
    router_prompt_template = "..." # Omitted for brevity, same as before
    captain_details = "\n".join([f"- **{c['name']}**: {c['description']}" for c in CAPTAIN_INFO])
    ROUTER_PROMPT = PromptTemplate(template=router_prompt_template, input_variables=["command"], partial_variables={"captains": captain_details, "format_instructions": parser.get_format_instructions()})
    router_chain = ROUTER_PROMPT | llm | parser
    routing_decision = router_chain.invoke({"command": command})
    captain_name = routing_decision.get("captain", "fallback")
    print(f"LLM decidió enrutar a: {captain_name}")
    return {"captain": captain_name}

print("Enrutador de capitanes para SG-SST definido y listo.")
