# activos_fijos/agents/corps/units/capitan_activos.py
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# Importar las herramientas tácticas de activos fijos
from activos_fijos.agents.tools.activos_fijos_tools import activos_fijos_tools

class AgentState(TypedDict):
    """Define el estado del agente."""
    messages: Annotated[list, lambda x, y: x + y]

class ActivosCaptain:
    """
    El 'Capitán de Activos Fijos' es un agente especializado en registrar
    nuevos activos y ejecutar los procesos de depreciación.
    """
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=api_key,
            max_retries=1
        ).bind_tools(activos_fijos_tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Construye el grafo de LangGraph."""
        graph = StateGraph(AgentState)

        graph.add_node("llm", self._call_llm)
        graph.add_node("tools", self._call_tool)

        graph.set_entry_point("llm")
        graph.add_conditional_edges(
            "llm",
            self._should_continue,
            {"continue": "tools", "end": END}
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
        """Llama al modelo de lenguaje."""
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def _call_tool(self, state: AgentState):
        """Ejecuta las herramientas solicitadas."""
        message = state["messages"][-1]
        tool_outputs = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.get("name")
            selected_tool = next((t for t in activos_fijos_tools if t.name == tool_name), None)
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
        """Punto de entrada para ejecutar una consulta."""
        initial_messages = [{"role": "system", "content": "Eres un asistente experto en gestión de activos fijos. Ayuda al usuario a registrar nuevos activos y a ejecutar la depreciación mensual. Para registrar un activo, necesitas saber todas sus cuentas contables asociadas; usa las herramientas de consulta del PUC si es necesario."},
                            {"role": "user", "content": query}]

        final_state = None
        for chunk in self.graph.stream({"messages": initial_messages}):
            final_state = chunk

        return final_state[list(final_state.keys())[-1]]['messages'][-1].content
