from typing import TypedDict, List, Any
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from agent.llm_service import get_llm

from .platoons.seguridad_inteligencia_teniente import get_seguridad_inteligencia_lieutenant_graph
from .platoons.expansion_institucional_teniente import get_expansion_institucional_lieutenant_graph

llm = get_llm()

class PlatformTask(BaseModel):
    task_description: str = Field(description="La descripción de la misión para el Teniente.")
    responsible_lieutenant: str = Field(
        description="El Teniente especialista. Debe ser: 'SeguridadInteligencia', 'ExpansionInstitucional'."
    )

class PlatformPlan(BaseModel):
    plan: List[PlatformTask]

class EstrategiaCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platform_plan: PlatformPlan | None
    task_queue: List[PlatformTask]
    completed_missions: list
    final_report: str
    error: str | None

seguridad_agent = get_seguridad_inteligencia_lieutenant_graph()
expansion_agent = get_expansion_institucional_lieutenant_graph()

async def create_platform_plan(state: EstrategiaCaptainState) -> EstrategiaCaptainState:
    print("--- 🧠 CAP. ESTRATEGIA Y PLATAFORMA: Creando Plan de Plataforma... ---")
    structured_llm = llm.with_structured_output(PlatformPlan)
    prompt = f"""
    Eres un Capitán de Estrategia y Plataforma. Tu Coronel te ha dado una orden.
    Descompónla en un plan de misiones para tus Tenientes.
    Tenientes bajo tu mando:
    - 'SeguridadInteligencia': Comanda la seguridad, la analítica y el agente de IA.
    - 'ExpansionInstitucional': Comanda la gestión de sedes, personal y sitio web.
    Analiza la orden y genera el plan en formato JSON: "{state['coronel_order']}"
    """
    try:
        plan = await structured_llm.ainvoke(prompt)
        print(f"--- 📝 CAP. ESTRATEGIA: Plan de Plataforma Generado. Pasos: {len(plan.plan)} ---")
        state.update({"platform_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    except Exception as e:
        state["error"] = f"No se pudo crear un plan de plataforma: {e}"
    return state

def route_to_lieutenant(state: EstrategiaCaptainState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    lieutenant_unit = state["task_queue"][0].responsible_lieutenant
    if lieutenant_unit == 'SeguridadInteligencia':
        return "seguridad_inteligencia_lieutenant"
    if lieutenant_unit == 'ExpansionInstitucional':
        return "expansion_institucional_lieutenant"
    state["task_queue"].pop(0)
    return "route_to_lieutenant"

async def seguridad_node(state: EstrategiaCaptainState) -> EstrategiaCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. SEGURIDAD E INTELIGENCIA -> '{mission.task_description}' ---")
    result = await seguridad_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({"lieutenant": "Seguridad e Inteligencia", "report": result.get("final_report", "Sin reporte.")})
    return state

async def expansion_node(state: EstrategiaCaptainState) -> EstrategiaCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. EXPANSIÓN INSTITUCIONAL -> '{mission.task_description}' ---")
    result = await expansion_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({"lieutenant": "Expansión Institucional", "report": result.get("final_report", "Sin reporte.")})
    return state

async def compile_final_report(state: EstrategiaCaptainState) -> EstrategiaCaptainState:
    print("--- 📄 CAP. ESTRATEGIA: Compilando Informe Estratégico para el Coronel... ---")
    if state.get("error"):
        report_body = f"Misión fallida. Razón: {state['error']}"
    else:
        report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión de Estrategia y Plataforma completada. Resumen:\n{report_body}"
    return state

def get_estrategia_plataforma_captain_graph():
    workflow = StateGraph(EstrategiaCaptainState)
    workflow.add_node("planner", create_platform_plan)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("seguridad_inteligencia_lieutenant", seguridad_node)
    workflow.add_node("expansion_institucional_lieutenant", expansion_node)
    workflow.add_node("compiler", compile_final_report)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router",
        route_to_lieutenant,
        {
            "seguridad_inteligencia_lieutenant": "seguridad_inteligencia_lieutenant",
            "expansion_institucional_lieutenant": "expansion_institucional_lieutenant",
            "compile_report": "compiler",
            "route_to_lieutenant": "router"
        }
    )
    workflow.add_edge("seguridad_inteligencia_lieutenant", "router")
    workflow.add_edge("expansion_institucional_lieutenant", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile().with_types(input_type=EstrategiaCaptainState)
