import os
import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from utils.micro_graph import MicroGraph, END
from .agent_state import AgentState
from .capitanes.capitan_periodos_contables import CapitanPeriodosContablesNode
from .capitanes.capitan_periodos_contables.equipos_tacticos.equipo_tactico_apertura_de_periodos.soldado import SoldadoAperturaPeriodoNode

class GeneralContableNode:
    """
    El nodo del General. Su responsabilidad es enrutar la tarea al Capitán correcto.
    """
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres el General del sistema de contabilidad. Tu única tarea es analizar la siguiente solicitud del usuario y decidir cuál de tus 15 capitanes es el más adecuado para manejarla. Debes responder únicamente con el nombre del nodo del capitán elegido de la siguiente lista: [capitan_plan_de_cuentas_y_politicas, capitan_periodos_contables, capitan_cuentas_por_cobrar_clientes, capitan_cuentas_por_pagar_proveedores, capitan_tesoreria_y_bancos, capitan_libro_diario_y_mayor, capitan_activos_fijos_contabilidad, capitan_nomina_contabilidad, capitan_inventarios_contabilidad, capitan_impuestos_sobre_las_ventas_iva, capitan_retenciones_y_otros_impuestos, capitan_cierre_mensual_y_anual, capitan_estados_financieros, capitan_presupuesto_y_control, capitan_auditoria_y_cumplimiento_niif]"),
            ("human", "{query}")
        ])
        self.chain = self.prompt | self.llm

    async def execute(self, state: AgentState) -> dict:
        print("--- Nodo General Contable ---")
        user_query = state['messages'][-1].content
        print(f"Analizando orden: '{user_query}'")

        response = await self.chain.ainvoke({"query": user_query})
        next_node = response.content.strip()

        print(f"Decisión del General: Delegar a '{next_node}'")

        valid_captains = [
            "capitan_plan_de_cuentas_y_politicas", "capitan_periodos_contables", "capitan_cuentas_por_cobrar_clientes",
            "capitan_cuentas_por_pagar_proveedores", "capitan_tesoreria_y_bancos", "capitan_libro_diario_y_mayor",
            "capitan_activos_fijos_contabilidad", "capitan_nomina_contabilidad", "capitan_inventarios_contabilidad",
            "capitan_impuestos_sobre_las_ventas_iva", "capitan_retenciones_y_otros_impuestos", "capitan_cierre_mensual_y_anual",
            "capitan_estados_financieros", "capitan_presupuesto_y_control", "capitan_auditoria_y_cumplimiento_niif"
        ]
        if next_node not in valid_captains:
            print(f"ADVERTENCIA: El LLM eligió un capitán inválido ('{next_node}'). Terminando flujo.")
            next_node = END

        return {"next": next_node}

class ContabilidadWorkflow:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no encontrada.")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0)
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = MicroGraph()

        # Nodos
        general_node = GeneralContableNode(self.llm)
        capitan_periodos_node = CapitanPeriodosContablesNode(self.llm)
        soldado_apertura_node = SoldadoAperturaPeriodoNode()

        workflow.add_node("general", general_node.execute)
        workflow.add_node("capitan_periodos_contables", capitan_periodos_node.execute)
        workflow.add_node("equipo_tactico_apertura_de_periodos", soldado_apertura_node.execute)

        def router(state: AgentState) -> str:
            return state["next"]

        workflow.set_entry_point("general")

        workflow.add_conditional_edge(
            "general",
            router,
            {
                "capitan_periodos_contables": "capitan_periodos_contables",
                END: END
            }
        )
        workflow.add_conditional_edge(
            "capitan_periodos_contables",
            router,
            {
                "equipo_tactico_apertura_de_periodos": "equipo_tactico_apertura_de_periodos",
                END: END
            }
        )
        workflow.add_edge("equipo_tactico_apertura_de_periodos", END)

        return workflow.compile()

    async def process_command(self, query: str):
        initial_state = {"messages": [HumanMessage(content=query)], "next": ""}
        final_state = await self.workflow.run(initial_state)
        print("\n--- ESTADO FINAL ---")
        print(final_state)
        return "Proceso completado."

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ADVERTENCIA: La variable de entorno OPENAI_API_KEY no está configurada.")
    else:
        workflow = ContabilidadWorkflow()
        comando = "Necesito abrir el periodo contable de Diciembre 2025"
        await workflow.process_command(comando)

if __name__ == '__main__':
    asyncio.run(main())
