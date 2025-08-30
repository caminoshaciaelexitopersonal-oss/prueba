import asyncio
import flet as ft
from agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph
from agents.corps.formacion_deportiva_colonel import get_formacion_deportiva_colonel_graph
from utils.database_manager import get_db_path
from utils.api_client import ApiClient
from agent.llm_service import get_llm

async def invoke_agent_for_area(page: ft.Page, area: str, user_input: str, user_id: int, tenant_id: int, tenant_api_key: str) -> str:
    """
    Invokes the correct top-level agent (Colonel) based on the area context.
    This is the main orchestration function.
    """
    print(f"--- 📞 Interfaz de Agente: Recibida solicitud para el área '{area}' ---")

    # 1. Instanciar el cliente de API
    # TODO: La URL base debería venir de una configuración, no estar hardcodeada.
    api_client = ApiClient(base_url="http://127.0.0.1:5001", tenant_api_key=tenant_api_key)

    # 2. Obtener la configuración de LLM para este inquilino
    llm_config = api_client.get_llm_config()
    if not llm_config:
        return "Error: No se pudo obtener la configuración de IA del servidor."

    # 3. Obtener la instancia de LLM correcta basada en la configuración del inquilino
    llm = get_llm(llm_config)
    if not llm:
        return "Error: No se pudo inicializar el modelo de lenguaje (LLM) para este inquilino."

    # 4. Obtener la ruta a la base de datos local del usuario para la memoria del agente
    db_path = get_db_path(page)

    # 5. Seleccionar y compilar el grafo del agente correcto, pasando el LLM y la DB path
    agent_graph = None
    if area == 'Cultura':
        agent_graph = get_formacion_cultura_colonel_graph(db_path, llm)
    elif area == 'Deportes':
        agent_graph = get_formacion_deportiva_colonel_graph(db_path, llm)
    else:
        return "Error: Área de asistente no reconocida."

    if agent_graph is None:
        return "Error: No se pudo construir el grafo del asistente de IA."

    # 6. Preparar el input y la configuración para la invocación
    graph_input = {"general_order": user_input, "app_context": {"user_id": user_id, "tenant_id": tenant_id}}
    config = {"configurable": {"thread_id": f"user_{user_id}"}}

    # 7. Invocar al agente
    try:
        print(f"--- 🚀 Invocando al Coronel de '{area}' con la orden: '{user_input[:50]}...' ---")
        final_state = await agent_graph.ainvoke(graph_input, config=config)
        report = final_state['messages'][-1].content if final_state.get('messages') else "El asistente completó la tarea pero no generó un informe final."
        print(f"--- ✅ Coronel de '{area}' completó la misión. ---")
        return report
    except Exception as e:
        print(f"--- ❌ Interfaz de Agente: Ocurrió un error crítico al invocar al Coronel. Error: {e} ---")
        return f"Lo siento, ocurrió un error inesperado al procesar tu solicitud. (Detalle: {e})"
