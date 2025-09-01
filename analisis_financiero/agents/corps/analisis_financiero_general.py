# analisis_financiero/agents/corps/analisis_financiero_general.py
"""
Define el grafo del agente General para el área de Análisis Financiero.
Este agente es un ENRUTADOR. Su única función es delegar tareas a los Capitanes especialistas.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# Importar los grafos de los capitanes subordinados
from .units.captain_comprehensive_analysis import get_comprehensive_analysis_captain_graph
from .units.captain_historical_trend import get_historical_trend_captain_graph

# 1. Definir el Estado del Grafo del General
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_request: str # La solicitud original del usuario

# 2. Definir las herramientas de delegación y el grafo principal
def get_analisis_financiero_general_graph(llm):
    """
    Construye y compila el grafo de LangGraph para el General de Análisis Financiero.
    """
    # Instanciar los grafos de los capitanes
    comprehensive_captain_agent = get_comprehensive_analysis_captain_graph(llm)
    historical_captain_agent = get_historical_trend_captain_graph(llm)

    # --- Herramientas de Delegación Reales ---
    @tool
    def delegate_to_comprehensive_analysis_captain(user_request: str) -> str:
        """
        Delega la tarea de generar un análisis financiero completo con todos los ratios para una fecha específica.
        """
        print(f"--- GENERAL (Análisis Fin.): Delegando a Capitán de Análisis Comprensivo. Solicitud: '{user_request}' ---")
        result = comprehensive_captain_agent({"user_request": user_request})
        return result['messages'][-1].content

    @tool
    def delegate_to_historical_trend_captain(user_request: str) -> str:
        """
        Delega la tarea de generar un historial de un ratio financiero específico a lo largo del tiempo.
        """
        print(f"--- GENERAL (Análisis Fin.): Delegando a Capitán de Tendencias. Solicitud: '{user_request}' ---")
        result = historical_captain_agent({"user_request": user_request})
        return result['messages'][-1].content

    general_tools = [delegate_to_comprehensive_analysis_captain, delegate_to_historical_trend_captain]

    model = llm.bind_tools(general_tools)

    # --- Nodos del Grafo del General ---
    def call_general_model(state):
        print("--- GENERAL (Análisis Fin.): Analizando orden... ---")
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_captain_tool(state):
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]

        tool_map = {tool.name: tool for tool in general_tools}
        selected_tool = tool_map.get(tool_call['name'])

        if not selected_tool:
            raise ValueError(f"Herramienta de delegación desconocida: {tool_call['name']}")

        print(f"--- GENERAL (Análisis Fin.): Invocando herramienta de delegación '{selected_tool.name}' ---")
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
        content="""Eres el General del Cuerpo de Análisis Financiero. Tu única misión es analizar la solicitud del usuario y delegarla al Capitán especialista apropiado.

- Si la solicitud es para **obtener un análisis completo de todos los ratios financieros** para una fecha, usa la herramienta `delegate_to_comprehensive_analysis_captain`.
- Si la solicitud es para **ver el historial, tendencia o evolución de un ratio específico** a lo largo del tiempo, usa la herramienta `delegate_to_historical_trend_captain`.
"""
    )

    def run_with_prompt(graph_input):
        initial_state = {
            "messages": [general_system_prompt, HumanMessage(content=graph_input["general_order"])],
            "user_request": graph_input["general_order"]
        }
        return app.invoke(initial_state, config=graph_input.get("config"))

    return run_with_prompt
