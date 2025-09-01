from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END, START
from agent.llm_service import get_llm
from langchain_core.pydantic_v1 import BaseModel, Field

from .squads.seguridad_sargento import get_seguridad_sargento_graph
from .squads.inteligencia_sargento import get_inteligencia_sargento_graph

llm = get_llm()

class SargentoMission(BaseModel):
    task_description: str = Field(description="La descripción específica de la misión para el Sargento.")
    responsible_sargento: str = Field(description="El Sargento especialista. Debe ser 'Seguridad' o 'Inteligencia'.")

class MissionPlan(BaseModel):
    plan: List[SargentoMission]

class SecurityIntelligenceState(TypedDict):
    captain_order: str
    app_context: Any
    mission_plan: MissionPlan | None
    task_queue: List[SargentoMission]
    completed_missions: list
    final_report: str
    error: str | None

seguridad_sargento_builder = get_seguridad_sargento_graph()
inteligencia_sargento_builder = get_inteligencia_sargento_graph()

async def planner_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    """Decide qué Sargento es necesario para cada fase de la misión."""
    print(f"--- 🤔 TTE. SEG/INT: Creando Plan de Pelotón para '{state['captain_order']}' ---")
    planner = llm.with_structured_output(MissionPlan)
    prompt = f"""
    Eres un Teniente de Seguridad e Inteligencia de Datos. Descompón la orden de tu Capitán en misiones para tus Sargentos.
    Sargentos Disponibles:
    - 'Seguridad': Experto en login, RBAC, auditoría y seguridad.
    - 'Inteligencia': Experto en analítica, dashboards y el agente de IA.
    Analiza la orden y crea el plan JSON: "{state['captain_order']}"
    """
    try:
        plan = await planner.ainvoke(prompt)
        state.update({"mission_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    except Exception as e:
        state["error"] = f"El Teniente no pudo crear un plan: {e}"
    return state

def router_node(state: SecurityIntelligenceState):
    """Dirige al Sargento correcto según el plan."""
    if state.get("error") or not state.get("task_queue"):
        return "compiler"
    sargento_unit = state["task_queue"][0].responsible_sargento
    if sargento_unit == "Seguridad":
        return "seguridad_sargento"
    if sargento_unit == "Inteligencia":
        return "inteligencia_sargento"
    state["task_queue"].pop(0)
    return "router"

async def seguridad_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    mission = state["task_queue"].pop(0)
    sargento_agent = seguridad_sargento_builder(state)
    result = await sargento_agent.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
    state["completed_missions"].append(f"Reporte del Sgto. de Seguridad: {result.get('final_report', 'Sin reporte.')}")
    return state

async def inteligencia_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    mission = state["task_queue"].pop(0)
    sargento_agent = inteligencia_sargento_builder(state)
    result = await sargento_agent.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
    state["completed_missions"].append(f"Reporte del Sgto. de Inteligencia: {result.get('final_report', 'Sin reporte.')}")
    return state

async def compiler_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    if state.get("error"):
        state["final_report"] = f"Misión fallida: {state['error']}"
    else:
        state["final_report"] = "Misión de Seguridad e Inteligencia completada.\n- " + "\n- ".join(state["completed_missions"])
    return state

def get_seguridad_inteligencia_lieutenant_graph():
    workflow = StateGraph(SecurityIntelligenceState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("seguridad_sargento", seguridad_node)
    workflow.add_node("inteligencia_sargento", inteligencia_node)
    workflow.add_node("compiler", compiler_node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router",
        router_node,
        {
            "seguridad_sargento": "seguridad_sargento",
            "inteligencia_sargento": "inteligencia_sargento",
            "compiler": "compiler",
            "router": "router"
        }
    )
    workflow.add_edge("seguridad_sargento", "router")
    workflow.add_edge("inteligencia_sargento", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile().with_types(input_type=SecurityIntelligenceState)
