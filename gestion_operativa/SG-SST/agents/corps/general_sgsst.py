import flet as ft
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# --- Importar Capitanes ---
from .capitanes.capitan_matriz_peligros import CapitanMatrizPeligros
# ... (otras importaciones de capitanes)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

class GeneralSGSST:
    def __init__(self, page: ft.Page):
        self.page = page

        # --- 1. Instanciar Capitanes DENTRO de __init__ ---
        # Ahora podemos pasarles 'page' si es necesario.
        self.capitan_matriz_peligros = CapitanMatrizPeligros(page=self.page)
        # self.capitan_planes = CapitanPlanesProcedimientos(page=self.page) # etc.

        # --- 2. Definir Herramientas como MÉTODOS de la clase ---
        # Usamos un truco con 'tool' para registrar métodos.
        tools = [
            tool(description="Delega tareas de identificación de peligros y evaluación de riesgos (IPERC).")(self.matriz_peligros_tool),
            # tool(description="...")(self.planes_procedimientos_tool),
        ]

        # --- 3. Configuración del Grafo (encapsulado) ---
        model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o", api_key=self.page.session.get("OPENAI_API_KEY"))
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
        print("General de SG-SST (con page y herramientas de instancia) listo.")

    # --- Definición de los métodos-herramienta ---
    def matriz_peligros_tool(self, tarea: str) -> str:
        """Herramienta que invoca al Capitán de Matriz de Peligros."""
        return self.capitan_matriz_peligros.ejecutar_mision(tarea)

    def process_command(self, orden: str):
        """Procesa una orden de alto nivel utilizando el grafo de LangGraph."""
        print(f"\nGeneral de SG-SST: Orden recibida - '{orden}'")

        # --- Flujo normal con LangGraph ---
        inputs = {"messages": [HumanMessage(content=orden)]}
        final_state = None
        for output in self.graph.stream(inputs):
            for key, value in output.items():
                print(f"--- Salida del nodo: {key} ---")
            final_state = output

        last_message = final_state['agent']['messages'][-1]
        result = last_message.content if isinstance(last_message.content, str) else str(last_message)
        print(f"General de SG-SST: Misión completada. Resultado: {result}")
        return result

# Bloque de prueba principal (no se usa en la app Flet)
if __name__ == '__main__':
    # Esta prueba ahora requeriría un objeto 'page' falso (mock),
    # por lo que se omite. La prueba real se hace ejecutando la app Flet.
    print("Para probar, ejecuta la aplicación Flet principal.")
