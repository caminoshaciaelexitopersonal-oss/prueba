from langchain_core.messages import ToolMessage
from .....tools import contabilidad_tools
from .....agent_state import AgentState

class SoldadoAperturaPeriodoNode:
    """
    El nodo del Soldado. Ejecuta una herramienta específica de forma asíncrona.
    """
    async def execute(self, state: AgentState) -> dict:
        print("--- Nodo Soldado (Apertura de Periodo) ---")
        order = state['messages'][0].content
        print(f"Ejecutando orden: '{order}'")

        try:
            # Asumimos que la herramienta también es async y la esperamos
            result = await contabilidad_tools.abrir_periodo_contable_tool.ainvoke({"query": order})
            tool_message = ToolMessage(content=result, name="abrir_periodo_contable")
            print(f"Herramienta ejecutada con éxito. Resultado: {result}")
        except Exception as e:
            error_message = f"Error al ejecutar la herramienta abrir_periodo_contable: {e}"
            tool_message = ToolMessage(content=error_message, name="abrir_periodo_contable")
            print(error_message)

        state['messages'].append(tool_message)
        return {"next": "__end__"}
