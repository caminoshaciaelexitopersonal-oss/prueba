# agents/corps/activos_fijos_general.py
"""
Define el grafo del agente General para el área de Activos Fijos.
Este agente es un ENRUTADOR. Su única función es delegar tareas a los Capitanes especialistas.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# Importar los grafos de los capitanes subordinados
from .units.captain_asset_reporting import get_asset_reporting_captain_graph
from .units.captain_asset_management import get_asset_management_captain_graph

# 1. Definir el Estado del Grafo del General
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_request: str # La solicitud original del usuario

# 2. Definir las herramientas de delegación y el grafo principal
def get_activos_fijos_general_graph(llm):
    """
    Construye y compila el grafo de LangGraph para el General de Activos Fijos,
    incluyendo la lógica para invocar a los capitanes especialistas.
    """
    # Instanciar los grafos de los capitanes
    reporting_captain_agent = get_asset_reporting_captain_graph(llm)
    management_captain_agent = get_asset_management_captain_graph(llm)

    # --- Herramientas de Delegación Reales ---
    @tool
    def delegate_to_asset_reporting_captain(user_request: str) -> str:
        """
        Delega la tarea de generar un reporte de activos fijos (ej: reporte de depreciación, listado de activos) al Capitán de Reportería de Activos.
        """
        print(f"--- GENERAL (Activos Fijos): Delegando a Capitán de Reportería. Solicitud: '{user_request}' ---")
        result = reporting_captain_agent({"user_request": user_request})
        return result['messages'][-1].content

    @tool
    def delegate_to_asset_management_captain(user_request: str) -> str:
        """
        Delega la tarea de gestionar un activo fijo (crear, dar de baja, modificar, depreciar) al Capitán de Gestión de Activos.
        """
        print(f"--- GENERAL (Activos Fijos): Delegando a Capitán de Gestión. Solicitud: '{user_request}' ---")
        result = management_captain_agent({"user_request": user_request})
        return result['messages'][-1].content

    general_tools = [delegate_to_asset_reporting_captain, delegate_to_asset_management_captain]

    model = llm.bind_tools(general_tools)

    # --- Nodos del Grafo del General ---
    def call_general_model(state):
        print("--- GENERAL (Activos Fijos): Analizando orden... ---")
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_captain_tool(state):
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]

        tool_map = {tool.name: tool for tool in general_tools}
        selected_tool = tool_map.get(tool_call['name'])

        if not selected_tool:
            raise ValueError(f"Herramienta de delegación desconocida: {tool_call['name']}")

        print(f"--- GENERAL (Activos Fijos): Invocando herramienta de delegación '{selected_tool.name}' ---")
        result = selected_tool.invoke(tool_call['args'])

        return {"messages": [HumanMessage(content=str(result), name="CaptainResponse")]}

    # --- Construcción del Grafo ---
    workflow = StateGraph(AgentState)
    workflow.add_node("general_af_router", call_general_model)
    workflow.add_node("captain_af_executor", call_captain_tool)

    workflow.set_entry_point("general_af_router")

    def should_delegate(state):
        if state['messages'][-1].tool_calls:
            return "continue"
        return "end"

    workflow.add_conditional_edges(
        "general_af_router",
        should_delegate,
        {"continue": "captain_af_executor", "end": END},
    )
    workflow.add_edge("captain_af_executor", END)

    app = workflow.compile()

    general_system_prompt = HumanMessage(
        content="""Eres el General del Cuerpo de Activos Fijos. Tu única misión es analizar la solicitud del usuario y delegarla al Capitán especialista apropiado.

- Si la solicitud es sobre **generar un reporte de activos, listado de activos o reporte de depreciación**, usa la herramienta `delegate_to_asset_reporting_captain`.
- Si la solicitud es sobre **crear un nuevo activo, dar de baja un activo, o calcular su depreciación**, usa la herramienta `delegate_to_asset_management_captain`.
"""
    )

    def run_with_prompt(graph_input):
        initial_state = {
            "messages": [general_system_prompt, HumanMessage(content=graph_input["general_order"])],
            "user_request": graph_input["general_order"]
        }
        return app.invoke(initial_state, config=graph_input.get("config"))

    return run_with_prompt
