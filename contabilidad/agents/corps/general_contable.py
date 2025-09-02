import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .agent_state import AgentState
from .capitanes.capitan_operaciones_diarias import CapitanOperacionesDiariasNode
# Se añadirán más importaciones de capitanes a medida que se implementen

load_dotenv()

class GeneralContableNode:
    """
    El nodo del General. Su responsabilidad es enrutar la tarea al Capitán correcto.
    """
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres el General del sistema de contabilidad. Tu única tarea es analizar la siguiente solicitud del usuario y decidir cuál de tus 10 capitanes es el más adecuado para manejarla. Debes responder únicamente con el nombre del nodo del capitán elegido de la siguiente lista: [capitan_operaciones_diarias, capitan_configuracion, capitan_procesos_cierre, capitan_tesoreria, capitan_estados_financieros, capitan_reportes_auxiliares, capitan_cumplimiento_auditoria, capitan_integraciones_documentos, capitan_presupuesto, capitan_impuestos]"),
            ("human", "{query}")
        ])
        self.chain = self.prompt | self.llm

    def execute(self, state: AgentState) -> dict:
        print("--- Nodo General Contable ---")
        user_query = state['messages'][-1].content
        print(f"Analizando orden: '{user_query}'")

        response = self.chain.invoke({"query": user_query})
        next_node = response.content.strip()

        print(f"Decisión del General: Delegar a '{next_node}'")

        valid_captains = ["capitan_operaciones_diarias", "capitan_configuracion", "capitan_procesos_cierre", "capitan_tesoreria", "capitan_estados_financieros", "capitan_reportes_auxiliares", "capitan_cumplimiento_auditoria", "capitan_integraciones_documentos", "capitan_presupuesto", "capitan_impuestos"]
        if next_node not in valid_captains:
            print(f"ADVERTENCIA: El LLM eligió un capitán inválido ('{next_node}'). Terminando flujo.")
            next_node = "end"

        return {"next": next_node}

class ContabilidadWorkflow:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no encontrada.")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0)
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        general_node = GeneralContableNode(self.llm)
        capitan_op_diarias_node = CapitanOperacionesDiariasNode(self.llm)

        workflow.add_node("general", general_node.execute)
        workflow.add_node("capitan_operaciones_diarias", capitan_op_diarias_node.execute)

        def router(state: AgentState) -> str:
            return state["next"]

        workflow.set_entry_point("general")
        workflow.add_conditional_edges(
            "general",
            router,
            {
                "capitan_operaciones_diarias": "capitan_operaciones_diarias",
                # Se añadirán las rutas a los otros 9 capitanes aquí
                "end": END
            }
        )
        workflow.add_edge("capitan_operaciones_diarias", END)

        return workflow.compile()

    def process_command(self, query: str):
        initial_state = {"messages": [HumanMessage(content=query)]}
        # Usamos stream para ver los eventos del grafo en tiempo real
        for event in self.workflow.stream(initial_state, {"recursion_limit": 10}):
            for key, value in event.items():
                print(f"Evento: {key}, Valor: {value}")
                print("---")
        return "Proceso completado."

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("ADVERTENCIA: La variable de entorno OPENAI_API_KEY no está configurada.")
    else:
        workflow = ContabilidadWorkflow()
        comando = "Necesito registrar una compra de suministros de oficina por 150.000 pesos de contado."
        workflow.process_command(comando)
