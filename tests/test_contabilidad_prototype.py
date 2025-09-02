import pytest
import os
from unittest.mock import MagicMock

# Establecer una variable de entorno ficticia para la prueba.
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "test_key_for_pytest"

# Mockear la clase ChatOpenAI ANTES de que sea importada por el módulo bajo prueba
from langchain_openai import ChatOpenAI
mock_llm_instance = MagicMock(spec=ChatOpenAI)
mock_response = MagicMock()
mock_response.content = "capitan_operaciones_diarias"
mock_llm_instance.invoke.return_value = mock_response

# Esto es un poco complejo: necesitamos reemplazar la clase ChatOpenAI antes de que se use.
# La forma más fácil es mockear el módulo entero.
from unittest.mock import patch

@patch('langchain_openai.ChatOpenAI', return_value=mock_llm_instance)
def test_prototype_workflow_execution(mock_chat_openai):
    """
    Prueba de integración para el flujo del prototipo de Contabilidad.
    Verifica que el workflow se puede crear y que puede procesar un comando
    sin lanzar excepciones, probando el flujo General -> Capitán.
    """
    # Asegurarse de que el directorio raíz esté en el path de Python
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        from contabilidad.agents.corps.general_contable import ContabilidadWorkflow

        # La instanciación ahora usará automáticamente el mock_llm_instance
        workflow_instance = ContabilidadWorkflow()

        # Ejecutar un comando de prueba
        comando = "Registrar una factura de compra."
        workflow_instance.process_command(comando)

    except Exception as e:
        pytest.fail(f"La ejecución del prototipo del workflow falló inesperadamente: {e}")
