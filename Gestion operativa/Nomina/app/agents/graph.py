from langgraph.graph import StateGraph, END
from .general import AgentState, general_agent
from .router import route_to_captain

# Define the graph that controls the agent flow for the payroll system
workflow = StateGraph(AgentState)

# Add the nodes to the graph
workflow.add_node("general", general_agent)
workflow.add_node("router", route_to_captain)

# Placeholder nodes for the payroll captains
def placeholder_captain(state: AgentState):
    print(f"---CAPTAIN NODE (NÓMINA): {state['captain']}---")
    return {"response": f"Task for payroll captain {state['captain']} would be executed here."}

workflow.add_node("master_data_captain", placeholder_captain)
workflow.add_node("contracts_captain", placeholder_captain)
workflow.add_node("fallback_node", lambda state: {"response": "No specific payroll captain could be found for this task."})


# Build the graph's edges
workflow.set_entry_point("general")
workflow.add_edge("general", "router")

# The conditional edge from the router to the captains
workflow.add_conditional_edges(
    "router",
    lambda state: state["captain"],
    {
        "master_data": "master_data_captain",
        "contracts": "contracts_captain",
        "fallback": "fallback_node"
    }
)

# All captain nodes lead to the end for now
workflow.add_edge("master_data_captain", END)
workflow.add_edge("contracts_captain", END)
workflow.add_edge("fallback_node", END)


# Compile the graph into a runnable app
app = workflow.compile()

print("LangGraph workflow for Nómina agents compiled.")

# Example of how to run it (for testing purposes)
if __name__ == '__main__':
    inputs = {"command": "Por favor, crea un nuevo empleado en el maestro."}
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")
