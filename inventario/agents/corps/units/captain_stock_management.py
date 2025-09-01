# agentes/corps/units/captain_stock_management.py
"""
Define el grafo del agente Capitán de Gestión de Stock.
Este agente es un especialista en crear productos y registrar movimientos de inventario.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ..tools.inventory_tools import (
    crear_nuevo_producto_tool,
    registrar_movimiento_stock_tool,
    importar_productos_desde_csv_tool,
)

# Herramientas específicas para este capitán
management_tools = [
    crear_nuevo_producto_tool,
    registrar_movimiento_stock_tool,
    importar_productos_desde_csv_tool,
]

# 1. Definir el Estado del Grafo
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Definir los Nodos del Grafo
def create_management_agent_graph(llm, tools):
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)

    def call_model(state):
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_tool(state):
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
def get_stock_management_captain_graph(llm):
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

    # Prompt del sistema para este Capitán
    management_captain_prompt = HumanMessage(
        content="""Eres un Capitán especialista en gestión de inventarios.
Tu misión es ejecutar tareas de creación de productos o registro de movimientos de stock.
Analiza la solicitud, extrae TODOS los parámetros necesarios y usa la herramienta apropiada.
Devuelve únicamente el resultado de la herramienta.
"""
    )

    def run_with_prompt(graph_input):
        initial_state = {"messages": [management_captain_prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
