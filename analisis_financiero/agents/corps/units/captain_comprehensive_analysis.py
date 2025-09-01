# agentes/corps/units/captain_comprehensive_analysis.py
"""
Define el grafo del agente Capitán de Análisis Comprensivo.
Este agente es un especialista en generar un análisis financiero completo.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ..tools.financial_analysis_tools import generar_analisis_completo_tool

# Herramientas específicas para este capitán
captain_tools = [generar_analisis_completo_tool]

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
        return {"messages": [HumanMessage(content=str(response), name="AnalysisTool")]}
    return model, tool_executor, call_model, call_tool

def should_continue(state):
    if state['messages'][-1].tool_calls:
        return "continue"
    return "end"

def get_comprehensive_analysis_captain_graph(llm):
    model, tool_executor, call_model_node, call_tool_node = create_agent_graph(llm, captain_tools)
    workflow = StateGraph(AgentState)
    workflow.add_node("analyst", call_model_node)
    workflow.add_node("action", call_tool_node)
    workflow.set_entry_point("analyst")
    workflow.add_conditional_edges(
        "analyst", should_continue, {"continue": "action", "end": END}
    )
    workflow.add_edge("action", "analyst")
    app = workflow.compile()

    prompt = HumanMessage(
        content="""Eres un Capitán especialista en análisis financiero. Tu única misión es generar un análisis completo de ratios para la fecha solicitada. Usa tu herramienta y devuelve el resultado."""
    )

    def run_with_prompt(graph_input):
        initial_state = {"messages": [prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
