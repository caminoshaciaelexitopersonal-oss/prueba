# agents/corps/units/captain_data_entry.py
"""
Define el grafo del agente Capitán de Entrada de Datos.
Este agente es un especialista en registrar transacciones contables.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from ....tools.contabilidad_tools import crear_asiento_contable_tool

# Herramientas específicas para este capitán
data_entry_tools = [crear_asiento_contable_tool]

# 1. Definir el Estado del Grafo
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Definir los Nodos del Grafo
def create_data_entry_agent_graph(llm, tools):
    """Crea el ejecutor de herramientas y el nodo del modelo para el Capitán."""
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)

    def call_model(state):
        """Invoca al LLM para que determine los detalles del asiento contable."""
        response = model.invoke(state['messages'])
        return {"messages": [response]}

    def call_tool(state):
        """Ejecuta la herramienta de creación de asiento contable."""
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]
        response = tool_executor.invoke(tool_call)
        return {"messages": [HumanMessage(content=str(response), name="DataEntryTool")]}

    return model, tool_executor, call_model, call_tool

def should_continue_data_entry(state):
    """Decide si el proceso de entrada de datos debe continuar."""
    if state['messages'][-1].tool_calls:
        return "continue"
    return "end"

# 3. Construir el Grafo del Capitán
def get_data_entry_captain_graph(llm):
    """
    Construye y compila el grafo de LangGraph para el Capitán de Entrada de Datos.
    """
    model, tool_executor, call_model_node, call_tool_node = create_data_entry_agent_graph(llm, data_entry_tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("data_entry_analyst", call_model_node)
    workflow.add_node("data_entry_action", call_tool_node)

    workflow.set_entry_point("data_entry_analyst")

    workflow.add_conditional_edges(
        "data_entry_analyst",
        should_continue_data_entry,
        {
            "continue": "data_entry_action",
            "end": END,
        },
    )

    workflow.add_edge("data_entry_action", "data_entry_analyst")

    app = workflow.compile()

    # El prompt del sistema para este Capitán especialista
    data_entry_captain_prompt = HumanMessage(
        content="""Eres un Capitán especialista en contabilidad y entrada de datos.
Tu misión es tomar una solicitud de transacción del usuario y convertirla en un asiento contable de partida doble preciso.

1.  Analiza la solicitud para entender la transacción (ej: compra de suministros, pago de factura, etc.).
2.  Determina las cuentas contables correctas que se afectan (débito y crédito). Deberás usar tu conocimiento contable para inferir las cuentas.
3.  Construye un asiento contable balanceado (la suma de débitos debe ser igual a la suma de créditos).
4.  Usa la herramienta `crear_asiento_contable_tool` con la descripción y la lista de movimientos que construiste.
5.  Devuelve únicamente el resultado de la herramienta. No necesitas presentarte.
"""
    )

    # Envolvemos 'app' para incluir el prompt y la orden
    def run_with_prompt(graph_input):
        # El input es la orden directa del General
        initial_state = {"messages": [data_entry_captain_prompt, HumanMessage(content=graph_input["user_request"])]}
        return app.invoke(initial_state)

    return run_with_prompt
