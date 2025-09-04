from langchain_core.messages import HumanMessage

# This file implements the logic for the General of the SG-SST system.

def general_sgsst_node(state):
    """
    This function is the entry point for the General's logic.
    It receives the initial user request and returns an update dictionary
    for the graph state, delegating to the appropriate captain.
    """
    print("---GENERAL (SG-SST) NODE RUNNING---")

    user_input = state['messages'][0].content
    print(f"General recibiendo orden del usuario: {user_input}")

    # Simple routing logic.
    if "peligro" in user_input.lower() or "riesgo" in user_input.lower():
        print("General delegando a Capitán de Matriz de Peligros.")
        order_for_captain = HumanMessage(
            content=user_input,
            name="Orden_del_General"
        )
        return {
            "messages": [order_for_captain],
            "next_agent": "capitan_matriz_peligros"
        }
    elif "inspeccion" in user_input.lower() or "inspeccionar" in user_input.lower():
        # Task is related to inspections. Delegate to the Safety Inspections Captain.
        print("General delegando a Capitán de Inspecciones de Seguridad.")
        order_for_captain = HumanMessage(
            content=user_input,
            name="Orden_del_General"
        )
        return {
            "messages": [order_for_captain],
            "next_agent": "capitan_inspecciones_seguridad"
        }
    else:
        unrecognized_task_message = HumanMessage(
            content=f"Orden no reconocida por el General: {user_input}",
            name="Error_General"
        )
        return {
            "messages": [unrecognized_task_message],
            "next_agent": "end"
        }
