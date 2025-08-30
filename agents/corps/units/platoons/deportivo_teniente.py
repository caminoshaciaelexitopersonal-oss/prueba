from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.deportivo_sargento import get_deportivo_sargento_graph

class DeportivoLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

deportivo_sargento_builder = get_deportivo_sargento_graph()

async def delegate_to_sargento(state: DeportivoLieutenantState) -> DeportivoLieutenantState:
    """Delega la misión completa al Sargento especialista en deportes."""
    order = state['captain_order']
    print(f"--- 🫡 TENIENTE DEPORTIVO: Recibida orden. Delegando misión al Sargento -> '{order}' ---")
    try:
        sargento_agent = deportivo_sargento_builder(state)
        result = await sargento_agent.ainvoke({
            "teniente_order": order,
            "app_context": state['app_context']
        })
        report_from_sargento = result.get("final_report", "El Sargento completó la misión sin un reporte detallado.")
        state["final_report"] = report_from_sargento
        print(f"--- ✔️ TENIENTE DEPORTIVO: El Sargento reporta misión cumplida. ---")
    except Exception as e:
        error_message = f"Misión fallida bajo el mando del Sargento Deportivo. Razón: {e}"
        print(f"--- ❌ TENIENTE DEPORTIVO: El Sargento reportó un error crítico: {error_message} ---")
        state["error"] = error_message
    return state

async def compile_report(state: DeportivoLieutenantState) -> DeportivoLieutenantState:
    """Prepara el informe final para el Capitán."""
    if state.get("error"):
        state["final_report"] = state["error"]
    print("--- 📄 TENIENTE DEPORTIVO: Informe para el Capitán de Operaciones Deportivas listo. ---")
    return state

def get_deportivo_lieutenant_graph():
    """Construye el agente LangGraph para el Teniente Deportivo."""
    workflow = StateGraph(DeportivoLieutenantState)
    workflow.add_node("delegate_mission_to_sargento", delegate_to_sargento)
    workflow.add_node("compile_final_report", compile_report)
    workflow.set_entry_point("delegate_mission_to_sargento")
    workflow.add_edge("delegate_mission_to_sargento", "compile_final_report")
    workflow.add_edge("compile_final_report", END)
    return workflow.compile().with_types(input_type=DeportivoLieutenantState)
