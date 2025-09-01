# agentes/corps/units/captain_asset_management.py
"""
Define el grafo del agente Capitán de Gestión de Activos.
Este agente es un especialista en registrar y depreciar activos fijos.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ..tools.asset_tools import (
    registrar_nuevo_activo_tool,
    ejecutar_depreciacion_mensual_tool,
)

# Herramientas específicas para este capitán
management_tools = [
    registrar_nuevo_activo_tool,
    ejecutar_depreciacion_mensual_tool,
]

# 1. Definir el Estado del Grafo
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Definir los Nodos del Grafo
def create_management_agent_graph(llm, tools):
    """Crea el ejecutor de herramientas y el nodo del modelo para el Capitán."""
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)

    def call_model(state):
        """Invoca al LLM para que decida qué herramienta de gestión usar."""
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_tool(state):
        """Ejecuta la herramienta de gestión seleccionada por el LLM."""
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]
        response = tool_executor.invoke(tool_call)
        return {"messages": [HumanMessage(content=str(response), name="ManagementTool")]}

    return model, tool_executor, call_model, call_tool

def should_continue_management(state):
    if state['messages'][-1].tool_calls:
        return "continue"
    return "end"

# 3. Construir el Grafo del Capitán
def get_asset_management_captain_graph(llm):
    """
    Construye y compila el grafo para el Capitán de Gestión de Activos.
    """
    model, tool_executor, call_model_node, call_tool_node = create_management_agent_graph(llm, management_tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("manager", call_model_node)
    workflow.add_node("management_action", call_tool_node)

    workflow.set_entry_point("manager")

    workflow.add_conditional_edges(
        "manager",
        should_continue_management,
        {"continue": "management_action", "end": END},
    )

    workflow.add_edge("management_action", "manager")

    app = workflow.compile()

    # Prompt del sistema para este Capitán especialista
    management_captain_prompt = HumanMessage(
        content="""Eres un Capitán especialista en gestión de activos fijos.
Tu misión es ejecutar tareas de creación o depreciación de activos.
Analiza la solicitud, extrae TODOS los parámetros necesarios y usa la herramienta apropiada.
Devuelve únicamente el resultado de la herramienta.
"""
    )

    def run_with_prompt(graph_input):
        initial_state = {"messages": [management_captain_prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
