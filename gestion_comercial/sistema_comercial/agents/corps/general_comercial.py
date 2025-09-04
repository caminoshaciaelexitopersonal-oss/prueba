import flet as ft
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import captains
from .capitanes.crm.capitan_registro_y_perfil_360 import CapitanRegistroPerfil360
from .capitanes.crm.capitan_oportunidades_y_pipeline import CapitanOportunidadesYPipeline

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

class GeneralComercial:
    def __init__(self, page: ft.Page, openai_api_key: str):
        self.page = page

        # Instantiate captains
        self.capitan_registro = CapitanRegistroPerfil360(page=self.page)
        self.capitan_pipeline = CapitanOportunidadesYPipeline(page=self.page)
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

        @tool
        def gestionar_pipeline_ventas(mision: str) -> str:
            """
            Use this tool for any task related to sales opportunities or leads, such as creating a new lead or updating its status.
            The 'mision' should be a string containing the detailed command, for example:
            "command='add', customer_id='some-uuid', source='website'"
            or "command='update', lead_id='another-uuid', new_status='contactado', new_pipeline_stage='negociacion'"
            """
            return self.capitan_pipeline.ejecutar_mision(mision)

        tools = [gestionar_perfil_cliente, gestionar_pipeline_ventas]

        # Configure the graph
        model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o", api_key=openai_api_key)
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

        # The final result is the content of the last ToolMessage
        # The 'action' node in the state contains the output of the ToolNode
        action = final_state.get('action', {})
        if action:
            tool_messages = action.get('messages', [])
            if tool_messages:
                result = tool_messages[-1].content
            else:
                 # If no tool output, return the last agent message
                last_agent_message = final_state.get('agent', {}).get('messages', [])[-1]
                result = last_agent_message.content if isinstance(last_agent_message.content, str) else str(last_agent_message)
        else:
            # If no action node, return the last agent message
            last_agent_message = final_state.get('agent', {}).get('messages', [])[-1]
            result = last_agent_message.content if isinstance(last_agent_message.content, str) else str(last_agent_message)

        print(f"General Comercial: Misión completada. Resultado: {result}")
        return result
