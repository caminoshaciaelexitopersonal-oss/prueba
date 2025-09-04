import flet as ft
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import the first captain
from .capitanes.crm.capitan_registro_y_perfil_360 import CapitanRegistroPerfil360

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

class GeneralComercial:
    def __init__(self, page: ft.Page):
        self.page = page

        # Instantiate captains
        self.capitan_registro = CapitanRegistroPerfil360(page=self.page)
        # ... other captains will be instantiated here in the future

        # Define tools for the general
        @tool
        def gestionar_perfil_cliente(mision: str) -> str:
            """
            Use this tool for any task related to adding, creating, getting, or viewing customer profiles.
            The 'mision' should be a string containing the detailed command, for example:
            "command='add', name='Jane Doe', email='jane.doe@email.com', phone='987654321'"
            or "command='get', customer_id='some-uuid-string'"
            """
            return self.capitan_registro.ejecutar_mision(mision)

        tools = [gestionar_perfil_cliente]

        # Configure the graph
        # NOTE: An API key needs to be configured in the environment for this to work.
        model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o")
        model = model.bind_tools(tools)

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", lambda state: {"messages": [model.invoke(state["messages"])]})
        workflow.add_node("action", ToolNode(tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            lambda state: "continue" if state['messages'][-1].tool_calls else "end",
            {"continue": "action", "end": END}
        )
        workflow.add_edge('action', 'agent')
        self.graph = workflow.compile()
        print("General Comercial: Listo y en servicio.")

    def process_command(self, orden: str):
        """
        Processes a high-level order using the LangGraph agent.
        """
        print(f"\nGeneral Comercial: Orden recibida - '{orden}'")
        inputs = {"messages": [HumanMessage(content=orden)]}

        final_state = None
        # The graph can be streamed to get intermediate steps
        for output in self.graph.stream(inputs):
            for key, value in output.items():
                print(f"--- Salida del nodo: {key} ---")
            final_state = output

        # The final result is usually in the last message from the agent
        last_message = final_state.get('agent', {}).get('messages', [])[-1]
        result = last_message.content if isinstance(last_message.content, str) else str(last_message)

        print(f"General Comercial: Misión completada. Resultado: {result}")
        return result
