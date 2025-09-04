# --- Environment Loading ---
from dotenv import load_dotenv
load_dotenv()
# --- End Environment Loading ---

from langgraph.graph import StateGraph, END
from .general import AgentState, general_agent
from .router import route_to_captain, CAPTAIN_INFO
# --- Import all implemented captains ---
from .captains.inspecciones_seguridad import captain_inspections_app
from .captains.matriz_peligros import captain_matriz_peligros_app
from .captains.planes_procedimientos import captain_planes_procedimientos_app

# A dictionary to map captain names to their compiled app
implemented_captains = {
    "inspecciones_seguridad": captain_inspections_app,
    "matriz_peligros": captain_matriz_peligros_app,
    "planes_procedimientos": captain_planes_procedimientos_app,
}

# --- Graph Definition ---
workflow = StateGraph(AgentState)
workflow.add_node("general", general_agent)
workflow.add_node("router", route_to_captain)

# --- Dynamic Captain Node Creation ---
def placeholder_captain_node(state: AgentState):
    captain = state.get('captain')
    # This node now directly returns the final response for the main graph
    return {"response": f"The '{captain}' captain is not yet implemented."}

captain_names = [c['name'] for c in CAPTAIN_INFO]
for name in captain_names:
    if name in implemented_captains:
        workflow.add_node(name, implemented_captains[name])
        print(f"SUCCESS: Real captain '{name}' plugged into the main graph.")
    else:
        workflow.add_node(name, placeholder_captain_node)

workflow.add_node("fallback", lambda state: {"response": "No specific captain could be found."})

# --- Edge Definition ---
workflow.set_entry_point("general")
workflow.add_edge("general", "router")
captain_mapping = {name: name for name in captain_names}
captain_mapping["fallback"] = "fallback"
workflow.add_conditional_edges("router", lambda state: state.get("captain", "fallback"), captain_mapping)

for name in captain_names:
    workflow.add_edge(name, END)
workflow.add_edge("fallback", END)

# --- Compile and Test ---
app = workflow.compile()
print(f"Dynamic LangGraph workflow updated. {len(implemented_captains)} captains are now live.")

if __name__ == '__main__':
    tests = {
        "Test 1: Inspección": "Necesito que crees una nueva inspección de seguridad.",
        "Test 2: Matriz de Peligros": "Por favor, crea una nueva matriz de peligros.",
        "Test 3: Planes y Procedimientos": "Elabora un nuevo PETS para trabajos en caliente.",
        "Test 4: Placeholder Captain (Documental)": "Archiva el manual de seguridad versión 3."
    }

    for test_name, command in tests.items():
        print(f"\n--- Running {test_name} ---")
        inputs = {"command": command}
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"Output from node '{key}': {value}")
            print("---")
