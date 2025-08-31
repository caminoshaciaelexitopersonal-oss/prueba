import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

# Import the new SG-SST tools
from tools.incident_tools import report_incident, list_incidents
from tools.risk_tools import add_risk, list_risks

# 1. Define the tools for the agent
incident_tools = [report_incident, list_incidents]
risk_tools = [add_risk, list_risks]
tools = incident_tools + risk_tools
tool_map = {tool.name: tool for tool in tools}

# 2. Define the model
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY environment variable not set. Agent will not work.")
    model = None
else:
    model = ChatOpenAI(temperature=0, streaming=True, api_key=api_key)
    model = model.bind_tools(tools)

# 3. Define the State (can be the same as the HR agent's state)
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

# 4. Define the Nodes (identical logic to the HR agent)
def call_model(state):
    if not model:
        return {"messages": [HumanMessage(content="Error: API Key no configurada.")]}
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

def call_tool(state):
    """Executes tool calls and returns the results."""
    last_message: AIMessage = state['messages'][-1]
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        if tool_name in tool_map:
            tool_function = tool_map[tool_name]
            tool_args = tool_call["args"]
            try:
                result = tool_function.invoke(tool_args)
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call['id']))
            except Exception as e:
                tool_messages.append(ToolMessage(content=f"Error executing tool {tool_name}: {e}", tool_call_id=tool_call['id']))
        else:
            tool_messages.append(ToolMessage(content=f"Error: Tool '{tool_name}' not found.", tool_call_id=tool_call['id']))
    return {"messages": tool_messages}

# 5. Define the Graph Logic (identical to the HR agent)
def should_continue(state):
    last_message = state['messages'][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "continue"

# 6. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "action", "end": END},
)
workflow.add_edge("action", "agent")

# 7. Compile the graph
app = workflow.compile()

# 8. Wrapper class
class SgsstAgent:
    def __init__(self):
        self.graph = app

    def invoke(self, query: str):
        if not model:
            yield {"messages": [HumanMessage(content="Error: OPENAI_API_KEY no está configurada.")]}
            return
        inputs = {"messages": [HumanMessage(content=query)]}
        yield from self.graph.stream(inputs, stream_mode="values")
