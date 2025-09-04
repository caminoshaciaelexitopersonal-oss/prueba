import pytest
import os
from langchain_core.messages import HumanMessage, ToolMessage

# Import the compiled graph application from the SG-SST module
from gestion_operativa.SG_SST.agent.graph import app, HierarchicalAgentState

# --- Test Fixture for Cleanup ---
@pytest.fixture
def cleanup_riesgos_file():
    """A pytest fixture to ensure the test environment is clean before and after the test."""
    # Setup: ensure the file doesn't exist before the test
    if os.path.exists("sgsst_riesgos.txt"):
        os.remove("sgsst_riesgos.txt")

    yield # This is where the test runs

    # Teardown: clean up the file after the test
    if os.path.exists("sgsst_riesgos.txt"):
        os.remove("sgsst_riesgos.txt")

# --- Test Function ---
def test_full_chain_of_command_poc(cleanup_riesgos_file):
    """
    Tests the full General -> Captain -> Lieutenant -> Tool execution chain.
    """
    # 1. Define the initial state for the test
    user_command = "Registrar nuevo peligro: Piso resbaladizo en bodega principal"
    initial_state: HierarchicalAgentState = {
        "messages": [HumanMessage(content=user_command, name="Entrada_Usuario")],
    }

    # 2. Run the graph to completion
    # We use .invoke() for tests as it directly returns the final state
    final_state = app.invoke(initial_state, {"recursion_limit": 10})

    # 3. Assert the results
    assert final_state is not None, "The final state should not be None"

    # Check that the graph reached the end state
    assert final_state.get('next_agent') == 'end', "The graph should end in the 'end' state"

    # Check the message history
    messages = final_state.get('messages', [])
    assert len(messages) > 3, "There should be several messages in the history"

    # The last message should be the output from the tool
    last_message = messages[-1]
    assert isinstance(last_message, ToolMessage), "The last message should be a ToolMessage"

    # Check the content of the tool's output message
    assert "Herramienta registrar_peligro ejecutada con éxito" in last_message.content, \
        "The tool execution success message should be in the final message"
    assert "Piso resbaladizo en bodega principal" in last_message.content, \
        "The original hazard description should be in the final message"

    # 4. Verify the side-effect (the file was written to)
    assert os.path.exists("sgsst_riesgos.txt"), "The sgsst_riesgos.txt file should have been created"
    with open("sgsst_riesgos.txt", "r") as f:
        content = f.read()
        assert "Piso resbaladizo en bodega principal" in content, "The file content should contain the hazard description"
