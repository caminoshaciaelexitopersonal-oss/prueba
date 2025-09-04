from langchain_core.messages import AIMessage
import uuid

# This file implements the logic for the Lieutenant of the Hazard Identification team.

def teniente_agent_node(state):
    """
    This function is the entry point for the lieutenant's logic.
    It receives the state and decides to use a tool by returning an AIMessage with tool_calls.
    """
    print("---TENIENTE (IDENTIFICACION DE PELIGROS) NODE RUNNING---")

    # Extract the specific instruction from the last message.
    last_message = state['messages'][-1]
    task_description = last_message.content

    print(f"Teniente ejecutando la tarea: {task_description}")

    # To request a tool call, the agent must output an AIMessage with the `tool_calls` attribute.
    # This signals to the graph that a tool needs to be executed.
    tool_call_request = AIMessage(
        content=f"Solicitando herramienta para registrar el peligro: '{task_description}'",
        tool_calls=[
            {
                "name": "registrar_peligro",
                "args": {"descripcion": task_description},
                "id": f"tool_call_{uuid.uuid4()}" # A unique ID for this tool call
            }
        ]
    )

    # We don't update the state directly. The node's return value is the update.
    # The graph will append this message to the state's message list.
    # We also need to tell the router where to go next.
    return {
        "messages": [tool_call_request],
        "next_agent": "tool_executor"
    }
