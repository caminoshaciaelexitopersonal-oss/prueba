import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el constructor del grafo del General
from contabilidad.agents.corps.contabilidad_colonel import get_contabilidad_colonel_graph

class TestAgentHierarchy(unittest.TestCase):

    @patch('contabilidad.agents.corps.contabilidad_colonel.get_data_entry_captain_graph')
    @patch('contabilidad.agents.corps.contabilidad_colonel.get_reporting_captain_graph')
    def test_delegation_to_reporting_captain(self, mock_get_reporting_captain, mock_get_data_entry_captain):
        """
        Verifica que una solicitud de reporte es delegada al Capitán de Reportería.
        """
        # --- Configuración del Mock ---
        # Simular los grafos de los capitanes y sus respuestas
        mock_reporting_agent = MagicMock()
        mock_reporting_agent.invoke.return_value = {"messages": [MagicMock(content="Reporte generado con éxito.")]}
        mock_get_reporting_captain.return_value = mock_reporting_agent

        mock_data_entry_agent = MagicMock()
        mock_get_data_entry_captain.return_value = mock_data_entry_agent

        # Simular el LLM
        mock_llm = MagicMock()
        # Configurar el LLM para que "decida" llamar a la herramienta de reportería
        mock_tool_call = MagicMock()
        mock_tool_call.name = "delegate_to_reporting_captain"
        mock_tool_call.args = {"user_request": "dame el balance general"}

        mock_llm_response = MagicMock()
        mock_llm_response.tool_calls = [mock_tool_call]
        mock_llm.bind_tools.return_value.invoke.return_value = mock_llm_response

        # --- Ejecución ---
        # Construir el grafo del General con el LLM simulado
        general_agent = get_contabilidad_colonel_graph(db_path="", llm=mock_llm)

        # Invocar al General
        general_agent({"general_order": "dame el balance general"})

        # --- Verificación ---
        # Verificar que el grafo del Capitán de Reportería fue invocado
        mock_reporting_agent.invoke.assert_called_once_with({"user_request": "dame el balance general"})

        # Verificar que el grafo del Capitán de Entrada de Datos NO fue invocado
        mock_data_entry_agent.invoke.assert_not_called()

    @patch('contabilidad.agents.corps.contabilidad_colonel.get_data_entry_captain_graph')
    @patch('contabilidad.agents.corps.contabilidad_colonel.get_reporting_captain_graph')
    def test_delegation_to_data_entry_captain(self, mock_get_reporting_captain, mock_get_data_entry_captain):
        """
        Verifica que una solicitud de registro de transacción es delegada al Capitán de Entrada de Datos.
        """
        # --- Configuración del Mock ---
        mock_reporting_agent = MagicMock()
        mock_get_reporting_captain.return_value = mock_reporting_agent

        mock_data_entry_agent = MagicMock()
        mock_data_entry_agent.invoke.return_value = {"messages": [MagicMock(content="Asiento creado con éxito.")]}
        mock_get_data_entry_captain.return_value = mock_data_entry_agent

        mock_llm = MagicMock()
        # Configurar el LLM para que "decida" llamar a la herramienta de entrada de datos
        mock_tool_call = MagicMock()
        mock_tool_call.name = "delegate_to_data_entry_captain"
        mock_tool_call.args = {"user_request": "registrar una compra de 100"}

        mock_llm_response = MagicMock()
        mock_llm_response.tool_calls = [mock_tool_call]
        mock_llm.bind_tools.return_value.invoke.return_value = mock_llm_response

        # --- Ejecución ---
        general_agent = get_contabilidad_colonel_graph(db_path="", llm=mock_llm)
        general_agent({"general_order": "registrar una compra de 100"})

        # --- Verificación ---
        # Verificar que el grafo del Capitán de Entrada de Datos fue invocado
        mock_data_entry_agent.invoke.assert_called_once_with({"user_request": "registrar una compra de 100"})

        # Verificar que el grafo del Capitán de Reportería NO fue invocado
        mock_reporting_agent.invoke.assert_not_called()

if __name__ == '__main__':
    unittest.main()
