from langchain_core.prompts import ChatPromptTemplate
from ..agent_state import AgentState

class CapitanPeriodosContablesNode:
    """
    El nodo del Capitán de Periodos Contables.
    Su responsabilidad es analizar la orden del General y delegarla al equipo táctico correcto.
    """
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres el Capitán de Periodos Contables. Tu única tarea es analizar la orden y decidir cuál de tus equipos tácticos debe ejecutarla. Responde únicamente con el nombre del equipo. Tus equipos son: [equipo_tactico_apertura_de_periodos, equipo_tactico_cierre_de_periodos, equipo_tactico_bloqueo_desbloqueo_de_periodos]."),
            ("human", "{query}")
        ])
        self.chain = self.prompt | self.llm

    async def execute(self, state: AgentState) -> dict:
        print("--- Nodo Capitán de Periodos Contables ---")
        order = state['messages'][-1].content
        print(f"Recibida orden del General: '{order}'")

        response = await self.chain.ainvoke({"query": order})
        next_node = response.content.strip()

        print(f"Decisión del Capitán: Delegar a '{next_node}'")

        valid_teams = ["equipo_tactico_apertura_de_periodos", "equipo_tactico_cierre_de_periodos", "equipo_tactico_bloqueo_desbloqueo_de_periodos"]
        if next_node not in valid_teams:
            print(f"ADVERTENCIA: Capitán eligió un equipo inválido ('{next_node}'). Terminando.")
            next_node = "__end__"

        return {"next": next_node}
