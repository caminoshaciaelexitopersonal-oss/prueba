# contabilidad/agents/corps/units/capitan_asientos.py
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.pydantic_v1 import BaseModel

# Importar las herramientas tácticas
from contabilidad.agents.tools.contabilidad_tools import contabilidad_tools

class AgentState(TypedDict):
    """Define el estado del agente. Los mensajes se acumulan."""
    messages: Annotated[list, lambda x, y: x + y]

class AsientosCaptain:
    """
    El 'Capitán de Asientos' es un agente especializado en el flujo de trabajo
    de crear comprobantes contables. Utiliza las herramientas tácticas para
    buscar información (como cuentas del PUC) y registrar la transacción.
    """
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=api_key,
            max_retries=1
        ).bind_tools(contabilidad_tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Construye el grafo de LangGraph que define el comportamiento del agente."""
        graph = StateGraph(AgentState)

        graph.add_node("llm", self._call_llm)
        graph.add_node("tools", self._call_tool)

        graph.set_entry_point("llm")
        graph.add_conditional_edges(
            "llm",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        graph.add_edge("tools", "llm")

        return graph.compile()

    def _should_continue(self, state: AgentState) -> str:
        """Decide si continuar llamando herramientas o finalizar."""
        if not state["messages"] or not isinstance(state["messages"][-1], BaseMessage):
            return "end"
        message = state["messages"][-1]
        if not message.tool_calls:
            return "end"
        else:
            return "continue"

    def _call_llm(self, state: AgentState):
        """Llama al modelo de lenguaje con el estado actual."""
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def _call_tool(self, state: AgentState):
        """Ejecuta las herramientas solicitadas por el LLM."""
        message = state["messages"][-1]
        tool_outputs = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.get("name")
            # Encontrar la herramienta correcta en la lista de herramientas
            selected_tool = next((t for t in contabilidad_tools if t.name == tool_name), None)
            if selected_tool:
                try:
                    output = selected_tool.invoke(tool_call.get("args"))
                except Exception as e:
                    output = f"Error al ejecutar la herramienta {tool_name}: {e}"
                tool_outputs.append({"tool_call_id": tool_call.get("id"), "content": str(output)})
            else:
                tool_outputs.append({"tool_call_id": tool_call.get("id"), "content": f"Error: Herramienta '{tool_name}' no encontrada."})

        return {"messages": tool_outputs}

    def run(self, query: str):
        """Punto de entrada para ejecutar una consulta a través del agente."""
        initial_messages = [{"role": "system", "content": "Eres un asistente experto en contabilidad. Tu objetivo es ayudar al usuario a registrar asientos contables. Primero, busca la información necesaria, como los códigos de cuenta del PUC. Luego, utiliza la herramienta 'registrar_comprobante_tool' para crear el asiento. Siempre confirma la operación al final."},
                            {"role": "user", "content": query}]

        # El método stream devuelve un generador, lo iteramos para obtener la respuesta final.
        final_state = None
        for chunk in self.graph.stream({"messages": initial_messages}):
            final_state = chunk

        # Devolver el último mensaje del asistente
        return final_state[list(final_state.keys())[-1]]['messages'][-1].content
