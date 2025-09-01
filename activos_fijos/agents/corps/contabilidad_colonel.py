# agents/corps/contabilidad_colonel.py
"""
Define el grafo del agente de más alto nivel para el área de Contabilidad.
Este agente (Coronel) orquesta el trabajo de agentes subordinados o herramientas.
"""
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from agents.tools.contabilidad_tools import contabilidad_tools

# 1. Definir el Estado del Grafo del Agente
# El estado es lo que se pasa entre los nodos del grafo.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Definir los Nodos del Grafo

def create_contabilidad_agent_graph(llm, tools):
    """Crea el ejecutor del agente y el nodo principal del modelo."""
    tool_executor = ToolExecutor(tools)
    model = llm.bind_tools(tools)

    def call_model(state):
        """El nodo 'cerebro': invoca al LLM para decidir el siguiente paso."""
        messages = state['messages']
        response = model.invoke(messages)
        # Devolvemos la respuesta del modelo para que el grafo la procese.
        # Si la respuesta contiene tool_calls, el siguiente nodo lo sabrá.
        return {"messages": [response]}

    def call_tool(state):
        """El nodo 'ejecutor': ejecuta las herramientas que el LLM decidió usar."""
        last_message = state['messages'][-1]

        # Iterar a través de las llamadas a herramientas que hizo el modelo
        tool_invocations = []
        for tool_call in last_message.tool_calls:
            action = (tool_call['name'], tool_call['args'])
            tool_invocations.append(action)

        # Ejecutar las herramientas y obtener las respuestas
        responses = tool_executor.batch(tool_invocations, return_exceptions=True)

        # Formatear las respuestas como ToolMessage para que el LLM las entienda
        tool_messages = [
            (f"Error al ejecutar la herramienta: {name}\n\n{response}",)
            if isinstance(response, Exception)
            else (f"Resultado de la herramienta: {name}\n\n{response}",)
            for (name, args), response in zip(tool_invocations, responses)
        ]

        return {"messages": tool_messages}

    return model, tool_executor, call_model, call_tool

def should_continue(state):
    """
    Arco condicional: Decide si continuar la ejecución o finalizar.
    Si el último mensaje del LLM tiene llamadas a herramientas, continúa.
    Si no, finaliza y devuelve la respuesta al usuario.
    """
    if state['messages'][-1].tool_calls:
        return "continue"
    else:
        return "end"

# 3. Construir el Grafo
def get_contabilidad_colonel_graph(db_path: str, llm):
    """
    Construye y compila el grafo de LangGraph para el agente de contabilidad.
    db_path: Ruta a la base de datos para posible memoria (no usado por ahora, pero mantenido por consistencia).
    llm: La instancia del modelo de lenguaje a usar.
    """
    # Crear los componentes del agente
    model, tool_executor, call_model_node, call_tool_node = create_contabilidad_agent_graph(llm, contabilidad_tools)

    # Definir el nuevo grafo
    workflow = StateGraph(AgentState)

    # Añadir los nodos al grafo
    workflow.add_node("agent", call_model_node)
    workflow.add_node("action", call_tool_node)

    # Definir el punto de entrada del grafo
    workflow.set_entry_point("agent")

    # Añadir los arcos condicionales
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )

    # Añadir un arco normal desde el nodo de acción de vuelta al agente
    workflow.add_edge("action", "agent")

    # Compilar el grafo en un ejecutable
    app = workflow.compile()

    # Añadir un paso inicial para dar la bienvenida al usuario
    # Esto no es parte del grafo, sino de la experiencia de usuario
    initial_prompt = HumanMessage(
        content="""Eres SARITA, un asistente de contabilidad experto.
        Tu misión es ayudar al usuario a entender sus datos financieros respondiendo a sus preguntas.
        Usa tus herramientas para obtener información de la base de datos.
        Sé concisa y directa en tus respuestas.
        El usuario ha iniciado el chat. Preséntate brevemente y pregunta en qué puedes ayudar."""
    )

    # Envolvemos 'app' para incluir el prompt inicial.
    # Esto es una simplificación. En una app real, el manejo del prompt inicial
    # se haría en la lógica de la vista de chat.
    def run_with_initial_prompt(graph_input):
        initial_state = {"messages": [initial_prompt, HumanMessage(content=graph_input["general_order"])]}
        return app.invoke(initial_state, config=graph_input.get("config"))

    # Devolvemos el grafo compilado. La interfaz de agente espera un objeto con un método 'invoke' o 'ainvoke'.
    # Devolver 'app' directamente es lo correcto. El manejo del prompt se hará en la UI.
    return app
