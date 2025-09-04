import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock

# Importar la clase del workflow
from contabilidad.agents.corps.general_contable import ContabilidadWorkflow

# Marcar esta prueba para que se omita si la API key de OpenAI no está disponible
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY no está configurada.")
@pytest.mark.asyncio
async def test_abrir_periodo_workflow(capsys):
    """
    Prueba el flujo completo de "Abrir periodo contable" usando el framework MicroGraph,
    verificando que la orden se delega correctamente a través de la cadena de mando.
    """
    # 1. Arrange: Preparar el entorno de la prueba
    comando = "Abrir el periodo contable de Enero 2026"

    # Mockear las respuestas de los LLM para aislar la prueba a la lógica del grafo
    # Mock para la decisión del General
    mock_general_response = MagicMock()
    mock_general_response.content = "capitan_periodos_contables"

    # Mock para la decisión del Capitán
    mock_capitan_response = MagicMock()
    mock_capitan_response.content = "equipo_tactico_apertura_de_periodos"

    # Usamos patch para interceptar las llamadas a 'ainvoke'
    with patch('contabilidad.agents.corps.general_contable.GeneralContableNode.chain.ainvoke', new_callable=MagicMock, return_value=mock_general_response) as mock_general_ainvoke, \
         patch('contabilidad.agents.corps.capitanes.capitan_periodos_contables.CapitanPeriodosContablesNode.chain.ainvoke', new_callable=MagicMock, return_value=mock_capitan_response) as mock_capitan_ainvoke, \
         patch('contabilidad.agents.tools.contabilidad_tools.abrir_periodo_contable_tool.ainvoke') as mock_tool_ainvoke:

        # Configuramos el mock de la herramienta para que devuelva un valor predecible
        mock_tool_ainvoke.return_value = "Éxito. El periodo 'Enero 2026' ha sido abierto."

        # 2. Act: Ejecutar el comando
        workflow = ContabilidadWorkflow()
        await workflow.process_command(comando)

    # 3. Assert: Verificar los resultados
    captured = capsys.readouterr()
    output = captured.out

    # Verificar que los nodos correctos fueron invocados en orden
    assert "--- Nodo General Contable ---" in output
    assert "Delegar a 'capitan_periodos_contables'" in output
    assert "--- Nodo Capitán de Periodos Contables ---" in output
    assert "Delegar a 'equipo_tactico_apertura_de_periodos'" in output
    assert "--- Nodo Soldado (Apertura de Periodo) ---" in output

    # Verificar que las cadenas de LLM fueron llamadas
    mock_general_ainvoke.assert_awaited_once_with({"query": comando})
    mock_capitan_ainvoke.assert_awaited_once_with({"query": comando})

    # Verificar que la herramienta fue llamada al final
    mock_tool_ainvoke.assert_awaited_once_with({"query": comando})

    # Verificar que el estado final se imprime (o el resultado de la herramienta)
    assert "Éxito. El periodo 'Enero 2026' ha sido abierto." in output
    assert "Ejecución del grafo finalizada." in output
