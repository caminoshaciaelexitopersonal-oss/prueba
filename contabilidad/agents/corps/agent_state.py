from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Define el estado compartido que fluye a través del grafo de agentes de contabilidad.

    Attributes:
        messages: El historial de mensajes de la conversación.
        next: El nombre del siguiente nodo (agente) a ejecutar.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
