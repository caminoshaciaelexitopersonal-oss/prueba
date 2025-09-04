from langchain_core.messages import AIMessage
import uuid

# This file implements the logic for the Lieutenant of the Facility Inspections team.

def teniente_inspecciones_instalaciones_node(state):
    """
    This function is the entry point for this lieutenant's logic.
    It receives an inspection task and calls the appropriate tool.
    """
    print("---TENIENTE (INSPECCIONES DE INSTALACIONES) NODE RUNNING---")

    last_message = state['messages'][-1]
    task_description = last_message.content

    print(f"Teniente de Inspecciones recibiendo tarea: {task_description}")

    # Simple parsing logic for the PoC. A real implementation would be more robust.
    # Example task: "Inspeccionar area: Taller Mecánico. Hallazgos: Extintor vencido, Falta de orden."
    try:
        area = task_description.split("area:")[1].split(".")[0].strip()
        hallazgos_str = task_description.split("Hallazgos:")[1].strip()
        hallazgos = [h.strip() for h in hallazgos_str.split(',')]
    except IndexError:
        area = "Área no especificada"
        hallazgos = ["Datos de inspección mal formados"]

    # Request the tool call via an AIMessage
    tool_call_request = AIMessage(
        content=f"Solicitando herramienta para registrar inspección en '{area}'",
        tool_calls=[
            {
                "name": "registrar_inspeccion",
                "args": {
                    "area_inspeccionada": area,
                    "hallazgos": hallazgos
                },
                "id": f"tool_call_{uuid.uuid4()}"
            }
        ]
    )

    return {
        "messages": [tool_call_request],
        "next_agent": "tool_executor"
    }
