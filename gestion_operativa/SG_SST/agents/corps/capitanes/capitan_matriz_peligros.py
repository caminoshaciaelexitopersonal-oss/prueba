from langchain_core.messages import HumanMessage

# This file implements the logic for the Captain of the Hazard Matrix team.

def capitan_matriz_peligros_node(state):
    """
    This function is the entry point for the captain's logic.
    It receives a task and returns an update dictionary, delegating to a tactical team.
    """
    print("---CAPITAN (MATRIZ DE PELIGROS) NODE RUNNING---")

    last_message = state['messages'][-1]
    task_description = last_message.content

    print(f"Capitán recibiendo tarea del General: {task_description}")

    # Simple routing logic.
    if "registrar" in task_description.lower() or "identificar" in task_description.lower():
        try:
            core_task = task_description.split(":", 1)[1].strip()
        except IndexError:
            core_task = "Tarea no especificada correctamente."

        print(f"Capitán delegando al Teniente de Identificación de Peligros. Tarea: '{core_task}'")

        order_for_lieutenant = HumanMessage(
            content=core_task,
            name="Orden_del_Capitan"
        )

        return {
            "messages": [order_for_lieutenant],
            "next_agent": "teniente_identificacion_peligros"
        }
    else:
        unrecognized_task_message = HumanMessage(
            content=f"Tarea no reconocida por el Capitán de Matriz de Peligros: {task_description}",
            name="Error_Capitan"
        )
        return {
            "messages": [unrecognized_task_message],
            "next_agent": "end"
        }
