# gestion_operativa/SG-SST/agents/corps/units/capitan_incidentes.py
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from gestion_operativa.SG_SST.agents.tools.sgsst_tools import sgsst_tools

class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

class IncidentesCaptain:
    """
    Capitán especializado en el registro, seguimiento e investigación
    de accidentes e incidentes laborales.
    """
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key).bind_tools(sgsst_tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("llm", self._call_llm)
        graph.add_node("tools", self._call_tool)
        graph.set_entry_point("llm")
        graph.add_conditional_edges(
            "llm", self._should_continue, {"continue": "tools", "end": END}
        )
        graph.add_edge("tools", "llm")
        return graph.compile()

    def _should_continue(self, state: AgentState):
        if not state["messages"] or not isinstance(state["messages"][-1], BaseMessage):
            return "end"
        if not state["messages"][-1].tool_calls:
            return "end"
        return "continue"

    def _call_llm(self, state: AgentState):
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def _call_tool(self, state: AgentState):
        message = state["messages"][-1]
        tool_outputs = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.get("name")
            selected_tool = next((t for t in sgsst_tools if t.name == tool_name), None)
            if selected_tool:
                try:
                    output = selected_tool.invoke(tool_call.get("args"))
                    tool_outputs.append({"tool_call_id": tool_call.get("id"), "content": str(output)})
                except Exception as e:
                    tool_outputs.append({"tool_call_id": tool_call.get("id"), "content": f"Error: {e}"})
            else:
                tool_outputs.append({"tool_call_id": tool_call.get("id"), "content": f"Error: Herramienta '{tool_name}' no encontrada."})
        return {"messages": tool_outputs}

    def run(self, query: str):
        initial_messages = [{"role": "system", "content": "Eres un Capitán del ejército de SG-SST, experto en la gestión de incidentes. Tu misión es ayudar al usuario a reportar nuevos incidentes y a consultar los existentes."},
                            {"role": "user", "content": query}]
        final_state = None
        for chunk in self.graph.stream({"messages": initial_messages}):
            final_state = chunk
        return final_state[list(final_state.keys())[-1]]['messages'][-1].content
