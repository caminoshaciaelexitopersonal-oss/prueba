# agentes/corps/units/captain_historical_trend.py
"""
Define el grafo del agente Capitán de Tendencias Históricas.
Este agente es un especialista en generar el historial de un ratio financiero específico.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ..tools.financial_analysis_tools import generar_historial_ratio_tool

# Herramientas específicas para este capitán
captain_tools = [generar_historial_ratio_tool]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def create_agent_graph(llm, tools):
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)
    def call_model(state):
        response = model.invoke(state['messages'])
        return {"messages": [response]}
    def call_tool(state):
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]
        response = tool_executor.invoke(tool_call)
        return {"messages": [HumanMessage(content=str(response), name="HistoryTool")]}
    return model, tool_executor, call_model, call_tool

def should_continue(state):
    if state['messages'][-1].tool_calls:
        return "continue"
    return "end"

def get_historical_trend_captain_graph(llm):
    model, tool_executor, call_model_node, call_tool_node = create_agent_graph(llm, captain_tools)
    workflow = StateGraph(AgentState)
    workflow.add_node("tracker", call_model_node)
    workflow.add_node("action", call_tool_node)
    workflow.set_entry_point("tracker")
    workflow.add_conditional_edges(
        "tracker", should_continue, {"continue": "action", "end": END}
    )
    workflow.add_edge("action", "tracker")
    app = workflow.compile()

    prompt = HumanMessage(
        content="""Eres un Capitán especialista en análisis de tendencias. Tu única misión es generar el historial de un ratio financiero específico a lo largo del tiempo. Extrae el nombre y la categoría del ratio de la solicitud, y usa tu herramienta."""
    )

    def run_with_prompt(graph_input):
        initial_state = {"messages": [prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
