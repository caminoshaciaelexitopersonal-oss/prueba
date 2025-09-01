# agents/corps/contabilidad_colonel.py
"""
Define el grafo del agente General (Coronel) para el área de Contabilidad.
Este agente es un ENRUTADOR. Su única función es delegar tareas a los Capitanes especialistas.
"""
import operator
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# Importar los grafos de los capitanes subordinados
from .units.captain_reporting import get_reporting_captain_graph
from .units.captain_data_entry import get_data_entry_captain_graph

# 1. Definir el Estado del Grafo del General
# Este estado se pasará a los sub-grafos (capitanes)
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_request: str # La solicitud original del usuario

# 2. Definir las herramientas de delegación y el grafo principal
def get_contabilidad_colonel_graph(db_path: str, llm):
    """
    Construye y compila el grafo de LangGraph para el General de Contabilidad,
    incluyendo la lógica para invocar a los capitanes especialistas.
    """
    # Instanciar los grafos de los capitanes
    reporting_captain_agent = get_reporting_captain_graph(llm)
    data_entry_captain_agent = get_data_entry_captain_graph(llm)

    # --- Herramientas de Delegación Reales ---
    # Estas herramientas ahora invocan los sub-grafos de los capitanes
    @tool
    def delegate_to_reporting_captain(user_request: str) -> str:
        """
        Delega la tarea de generar un reporte financiero al Capitán de Reportería.
        Usa esta herramienta si el usuario pide un balance, estado de resultados, o cualquier otro tipo de reporte financiero.
        """
        print(f"--- GENERAL: Delegando a Capitán de Reportería. Solicitud: '{user_request}' ---")
        # Invocar el sub-grafo del capitán
        result = reporting_captain_agent.invoke({"user_request": user_request})
        # La respuesta final del capitán está en su último mensaje
        return result['messages'][-1].content

    @tool
    def delegate_to_data_entry_captain(user_request: str) -> str:
        """
        Delega la tarea de registrar una transacción contable al Capitán de Entrada de Datos.
        Usa esta herramienta si el usuario pide registrar una compra, una venta, un pago, o cualquier otra transacción.
        """
        print(f"--- GENERAL: Delegando a Capitán de Entrada de Datos. Solicitud: '{user_request}' ---")
        # Invocar el sub-grafo del capitán
        result = data_entry_captain_agent.invoke({"user_request": user_request})
        # La respuesta final del capitán está en su último mensaje
        return result['messages'][-1].content

    general_tools = [delegate_to_reporting_captain, delegate_to_data_entry_captain]

    # Vincular las herramientas al modelo del General
    model = llm.bind_tools(general_tools)

    # --- Nodos del Grafo del General ---
    def call_general_model(state):
        """Invoca al LLM del General para que decida a qué Capitán delegar."""
        print("--- GENERAL: Analizando orden... ---")
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_captain_tool(state):
        """Ejecuta la herramienta de delegación, que a su vez invoca a un Capitán."""
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]

        tool_map = {tool.name: tool for tool in general_tools}
        selected_tool = tool_map.get(tool_call['name'])

        if not selected_tool:
            raise ValueError(f"Herramienta de delegación desconocida: {tool_call['name']}")

        print(f"--- GENERAL: Invocando herramienta de delegación '{selected_tool.name}' ---")
        result = selected_tool.invoke(tool_call['args'])

        return {"messages": [HumanMessage(content=str(result), name="CaptainResponse")]}

    # --- Construcción del Grafo ---
    workflow = StateGraph(AgentState)
    workflow.add_node("general_router", call_general_model)
    workflow.add_node("captain_executor", call_captain_tool)

    workflow.set_entry_point("general_router")

    def should_delegate(state):
        if state['messages'][-1].tool_calls:
            return "continue"
        return "end"

    workflow.add_conditional_edges(
        "general_router",
        should_delegate,
        {"continue": "captain_executor", "end": END},
    )
    workflow.add_edge("captain_executor", END) # El trabajo del General termina después de la delegación

    app = workflow.compile()

    # Prompt del sistema para el General
    general_system_prompt = HumanMessage(
        content="""Eres el General del Cuerpo de Contabilidad. Tu única misión es analizar la solicitud del usuario y delegarla al Capitán especialista apropiado. No respondas directamente al usuario ni pidas clarificación. Solo delega.

- Si la solicitud es para **generar un reporte o estado financiero**, usa la herramienta `delegate_to_reporting_captain`.
- Si la solicitud es para **registrar una transacción o asiento contable**, usa la herramienta `delegate_to_data_entry_captain`.
"""
    )

    # Envolvemos 'app' para la invocación final
    def run_with_prompt(graph_input):
        initial_state = {
            "messages": [general_system_prompt, HumanMessage(content=graph_input["general_order"])],
            "user_request": graph_input["general_order"]
        }
        return app.invoke(initial_state, config=graph_input.get("config"))

    return run_with_prompt
