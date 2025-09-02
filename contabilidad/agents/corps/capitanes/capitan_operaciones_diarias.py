from langchain_core.messages import HumanMessage
from ..agent_state import AgentState

class CapitanOperacionesDiariasNode:
    """
    Nodo para el Capitán de Operaciones Diarias.
    Recibe órdenes del General y las delega a sus pelotones.
    """
    def __init__(self, llm):
        self.llm = llm

    def execute(self, state: AgentState) -> dict:
        """
        Lógica del Capitán de Operaciones Diarias.
        """
        print("--- Nodo Capitán Operaciones Diarias ---")
        print("Misión recibida del General. Analizando tarea.")

        # En el futuro, este nodo decidirá a qué pelotón delegar
        # (ej. 'asientos_contables' o 'libros_y_diarios').
        next_node = "end" # Por ahora, el flujo termina aquí.

        return {
            "messages": [HumanMessage(content="Capitán de Operaciones Diarias: Misión recibida y en proceso.")],
            "next": next_node
        }
