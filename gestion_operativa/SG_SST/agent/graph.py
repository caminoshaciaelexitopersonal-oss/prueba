from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
import operator

# --- Import Agent Logic ---
from gestion_operativa.SG_SST.agents.corps.general_sgsst import general_sgsst_node
from gestion_operativa.SG_SST.agents.corps.capitanes.capitan_matriz_peligros import capitan_matriz_peligros_node
from gestion_operativa.SG_SST.agents.corps.capitanes.equipos_tacticos.matriz_peligros.identificacion_peligros.teniente import teniente_agent_node
from gestion_operativa.SG_SST.agents.corps.capitanes.capitan_inspecciones_seguridad import capitan_inspecciones_node
from gestion_operativa.SG_SST.agents.corps.capitanes.equipos_tacticos.inspecciones_seguridad.inspecciones_instalaciones.teniente import teniente_inspecciones_instalaciones_node

# --- Import Tools ---
from gestion_operativa.SG_SST.tools.sgsst_tools import registrar_peligro, registrar_inspeccion

tools = [registrar_peligro, registrar_inspeccion]
tool_map = {tool.name: tool for tool in tools}

# --- Agent State ---
class HierarchicalAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: str

# --- Node Implementations ---
def tool_executor_node(state: HierarchicalAgentState) -> dict:
    print("---TOOL EXECUTOR NODE RUNNING---")
    last_message = state['messages'][-1]

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"next_agent": "end"}

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]

    if tool_name in tool_map:
        tool_function = tool_map[tool_name]
        tool_args = tool_call["args"]
        try:
            print(f"Ejecutando herramienta '{tool_name}' con argumentos: {tool_args}")
            result = tool_function.invoke(tool_args)
            result_message = f"Herramienta {tool_name} ejecutada con éxito. Resultado: {result}"
        except Exception as e:
            result_message = f"Error ejecutando la herramienta {tool_name}: {e}"
    else:
        result_message = f"Error: Herramienta '{tool_name}' no encontrada."

    tool_output_message = ToolMessage(
        content=result_message,
        tool_call_id=tool_call['id']
    )

    return {
        "messages": [tool_output_message],
        "next_agent": "end"
    }

# --- Graph Definition ---
workflow = StateGraph(HierarchicalAgentState)

# Add nodes for all agents
workflow.add_node("general", general_sgsst_node)
workflow.add_node("tool_executor", tool_executor_node)
# PoC Captain 1
workflow.add_node("capitan_matriz_peligros", capitan_matriz_peligros_node)
workflow.add_node("teniente_identificacion_peligros", teniente_agent_node)
# New Captain 2
workflow.add_node("capitan_inspecciones_seguridad", capitan_inspecciones_node)
workflow.add_node("teniente_inspecciones_instalaciones", teniente_inspecciones_instalaciones_node)

def router(state: HierarchicalAgentState) -> str:
    print(f"---ROUTING TO: {state['next_agent']}---")
    if state['next_agent'] == 'end':
        return END
    return state['next_agent']

workflow.set_entry_point("general")
# Connect all nodes to the router
workflow.add_conditional_edges("general", router)
workflow.add_conditional_edges("capitan_matriz_peligros", router)
workflow.add_conditional_edges("teniente_identificacion_peligros", router)
workflow.add_conditional_edges("capitan_inspecciones_seguridad", router)
workflow.add_conditional_edges("teniente_inspecciones_instalaciones", router)
workflow.add_conditional_edges("tool_executor", router)

app = workflow.compile()

# --- Main Execution Block for Testing ---
if __name__ == '__main__':

    def run_test(test_name, command):
        print(f"\n--- INICIANDO PRUEBA: {test_name} ---")
        initial_state = {"messages": [HumanMessage(content=command, name="Entrada_Usuario")]}
        print(f"Comando inicial: '{command}'\n")

        final_state = None
        for event in app.stream(initial_state, {"recursion_limit": 10}):
            if "__end__" not in event:
                node_name = list(event.keys())[0]
                final_state = event[node_name]

        print("\n--- PRUEBA FINALIZADA ---")
        print("Historial de mensajes final:")
        if final_state:
            for message in final_state.get('messages', []):
                print(f"- {message.__class__.__name__}: {message.content}")
        else:
            print("No se pudo capturar un estado final válido.")
        print("-" * 20)

    # Test 1: Original PoC for Hazard Reporting
    run_test(
        "Reporte de Peligro",
        "Registrar nuevo peligro: Piso resbaladizo en bodega principal"
    )

    # Test 2: New workflow for Safety Inspections
    run_test(
        "Registro de Inspección",
        "Realizar inspección de seguridad en area: Taller Mecánico. Buscar hallazgos: Extintor vencido, Falta de orden."
    )
