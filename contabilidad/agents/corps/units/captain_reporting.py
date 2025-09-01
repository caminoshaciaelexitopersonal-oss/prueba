# agents/corps/units/captain_reporting.py
"""
Define el grafo del agente Capitán de Reportería.
Este agente es un especialista en generar reportes financieros.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ....tools.contabilidad_tools import (
    generar_balance_general_tool,
    generar_estado_resultados_tool,
    generar_balance_comprobacion_tool,
)

# Herramientas específicas para este capitán
reporting_tools = [
    generar_balance_general_tool,
    generar_estado_resultados_tool,
    generar_balance_comprobacion_tool,
]

# 1. Definir el Estado del Grafo
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Definir los Nodos del Grafo
def create_reporting_agent_graph(llm, tools):
    """Crea el ejecutor de herramientas y el nodo del modelo para el Capitán."""
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)

    def call_model(state):
        """Invoca al LLM para que decida qué herramienta de reporte usar."""
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_tool(state):
        """Ejecuta la herramienta de reporte seleccionada por el LLM."""
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]
        response = tool_executor.invoke(tool_call)
        return {"messages": [HumanMessage(content=str(response), name="ReportingTool")]}

    return model, tool_executor, call_model, call_tool

def should_continue_reporting(state):
    """Decide si el reporteo debe continuar."""
    if state['messages'][-1].tool_calls:
        return "continue"
    return "end"

# 3. Construir el Grafo del Capitán
def get_reporting_captain_graph(llm):
    """
    Construye y compila el grafo de LangGraph para el Capitán de Reportería.
    """
    model, tool_executor, call_model_node, call_tool_node = create_reporting_agent_graph(llm, reporting_tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("reporter", call_model_node)
    workflow.add_node("reporting_action", call_tool_node)

    workflow.set_entry_point("reporter")

    workflow.add_conditional_edges(
        "reporter",
        should_continue_reporting,
        {
            "continue": "reporting_action",
            "end": END,
        },
    )

    workflow.add_edge("reporting_action", "reporter")

    app = workflow.compile()

    # El prompt del sistema para este Capitán especialista
    reporting_captain_prompt = HumanMessage(
        content="""Eres un Capitán especialista en reportería contable.
Tu única misión es generar el reporte financiero exacto que se te solicita.
Usa tus herramientas para generar la información y devuelve el resultado directamente.
No necesitas presentarte, solo ejecuta la orden.
"""
    )

    # Envolvemos 'app' para incluir el prompt y la orden
    def run_with_prompt(graph_input):
        # El input es la orden directa del General
        initial_state = {"messages": [reporting_captain_prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
