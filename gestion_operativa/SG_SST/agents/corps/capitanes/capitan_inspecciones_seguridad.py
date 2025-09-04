from langchain_core.messages import HumanMessage

# This file implements the logic for the Captain of the Safety Inspections team.

def capitan_inspecciones_node(state):
    """
    Receives an inspection-related task from the General and delegates it
    to the appropriate tactical team.
    """
    print("---CAPITAN (INSPECCIONES DE SEGURIDAD) NODE RUNNING---")

    last_message = state['messages'][-1]
    task_description = last_message.content

    print(f"Capitán de Inspecciones recibiendo tarea: {task_description}")

    # Simple routing. If the task involves inspecting a facility/area,
    # delegate to the facility inspections team.
    if "inspeccion" in task_description.lower() and ("area" in task_description.lower() or "instalacion" in task_description.lower()):

        # For this PoC, we'll assume the General's order can be reformatted for the lieutenant.
        # A real system might use an LLM to parse and structure this.
        # Example input: "Realizar inspección de seguridad en area: Taller Mecánico. Buscar hallazgos: Extintor vencido, Falta de orden."
        try:
            # Reformat the task into the structure the lieutenant expects.
            area = task_description.split("area:")[1].split(".")[0].strip()
            hallazgos = task_description.split("hallazgos:")[1].strip()
            formatted_task = f"Inspeccionar area: {area}. Hallazgos: {hallazgos}"
        except IndexError:
            formatted_task = "Inspeccionar area: Desconocida. Hallazgos: Tarea del General mal formada."

        print(f"Capitán delegando a Teniente de Inspecciones de Instalaciones.")

        order_for_lieutenant = HumanMessage(
            content=formatted_task,
            name="Orden_del_Capitan_Inspecciones"
        )

        return {
            "messages": [order_for_lieutenant],
            "next_agent": "teniente_inspecciones_instalaciones"
        }
    else:
        # Handle other types of inspections (equipment, EPP) here in the future
        unrecognized_task_message = HumanMessage(
            content=f"Tipo de inspección no reconocida por el Capitán: {task_description}",
            name="Error_Capitan_Inspecciones"
        )
        return {
            "messages": [unrecognized_task_message],
            "next_agent": "end"
        }
