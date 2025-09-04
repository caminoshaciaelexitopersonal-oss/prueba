from .general import AgentState

# This list will eventually be populated with the 15 payroll captains
# For now, it's a placeholder.
CAPTAIN_DESCRIPTIONS = {
    "master_data": "Responsable de la creación y mantenimiento del maestro de empleados.",
    "contracts": "Responsable de la administración del ciclo de vida de los contratos.",
    # ... add all 15 captains here later
}

def route_to_captain(state: AgentState):
    """
    A simple router that decides which payroll captain to send the task to.
    In the future, this will be a sophisticated LangChain router.
    """
    print("---CAPTAIN ROUTER (NÓMINA)---")
    command = state.get("command", "").lower()

    # This is a placeholder for the real routing logic
    if "empleado" in command or "maestro" in command:
        print("Routing to: Captain_Datos_Maestros")
        return {"captain": "master_data"}
    elif "contrato" in command or "contratar" in command:
        print("Routing to: Captain_Contratos")
        return {"captain": "contracts"}
    else:
        print("Routing to: Fallback/General")
        return {"captain": "fallback"}

print("Captain router for Nómina defined.")
