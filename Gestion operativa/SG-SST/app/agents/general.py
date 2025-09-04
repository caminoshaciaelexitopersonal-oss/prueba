from typing import TypedDict, Annotated
import operator

# This will be the state of our graph
class AgentState(TypedDict):
    # The user's command
    command: str
    # The name of the captain to route to
    captain: str
    # The response from the agent
    response: str

def general_agent(state: AgentState):
    """
    This is the entry point agent, the 'General'.
    Its primary job is to receive the command and pass it to the router.
    """
    print("---GENERAL AGENT---")
    command = state.get("command", "")
    print(f"Received command: {command}")
    # For now, we do nothing but prepare for routing
    return {"command": command}

print("General agent for SG-SST defined.")
