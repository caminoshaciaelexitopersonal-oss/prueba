# gestion_operativa/SG-SST/agents/corps/general_sgsst.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Importar todos los capitanes
from .units.capitan_matriz_peligros import PeligrosCaptain
from .units.capitan_planes import PlanesCaptain
from .units.capitan_documentacion import DocumentacionCaptain
from .units.capitan_capacitacion import CapacitacionCaptain
from .units.capitan_incidentes import IncidentesCaptain
from .units.capitan_indicadores import IndicadoresCaptain
from .units.capitan_biblioteca import BibliotecaCaptain
from .units.capitan_comunicaciones import ComunicacionesCaptain

load_dotenv()

class GeneralSGSST:
    """
    El General de SG-SST. Su función principal es actuar como un enrutador inteligente,
    delegando las órdenes del usuario al Capitán más adecuado.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        # El General tiene a todos sus Capitanes bajo su mando
        self.captains = {
            "Matriz de Peligros": PeligrosCaptain(api_key=api_key),
            "Planes y Procedimientos": PlanesCaptain(api_key=api_key),
            "Documentación y Formatos": DocumentacionCaptain(api_key=api_key),
            "Capacitación": CapacitacionCaptain(api_key=api_key),
            "Incidentes e Investigación": IncidentesCaptain(api_key=api_key),
            "Indicadores y Dashboards": IndicadoresCaptain(api_key=api_key),
            "Biblioteca y Normatividad": BibliotecaCaptain(api_key=api_key),
            "Comunicaciones y Señalética": ComunicacionesCaptain(api_key=api_key),
        }

        # Crear el LLM y la cadena de enrutamiento
        self.router_prompt = self._create_router_prompt()
        self.router_chain = self.router_prompt | ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key) | StrOutputParser()

    def _create_router_prompt(self):
        """Crea el prompt que el General usa para decidir a qué Capitán enrutar."""
        template = """Eres el General del ejército de SG-SST. Tu misión es enrutar la orden de un usuario al Capitán correcto.
        Analiza la siguiente orden y responde ÚNICAMENTE con el nombre del Capitán más adecuado de la siguiente lista.

        Aquí están tus Capitanes y sus especialidades:

        - **Matriz de Peligros**: Para todo lo relacionado con identificar, valorar y registrar riesgos (IPERC).
        - **Planes y Procedimientos**: Para crear o modificar el plan anual de SG-SST, planes de emergencia o procedimientos de trabajo seguro.
        - **Documentación y Formatos**: Para crear o buscar formatos, checklists, manuales, etc.
        - **Capacitación**: Para registrar capacitaciones, inducciones o entregas de EPP a los empleados.
        - **Incidentes e Investigación**: Para reportar o consultar accidentes e incidentes de trabajo.
        - **Indicadores y Dashboards**: Para definir o consultar los indicadores de gestión (KPIs) del sistema.
        - **Biblioteca y Normatividad**: Para archivar o buscar documentos legales o libros técnicos.
        - **Comunicaciones y Señalética**: Para redactar políticas, reglamentos o generar textos para señalización.

        Orden del usuario:
        "{query}"

        Capitán seleccionado:"""
        return ChatPromptTemplate.from_template(template)

    def _route_to_captain(self, query: str) -> str:
        """Usa el LLM para determinar el Capitán correcto."""
        captain_name = self.router_chain.invoke({"query": query}).strip()

        # Validar que la respuesta del LLM sea uno de los capitanes
        if captain_name in self.captains:
            return captain_name
        else:
            # Si el LLM falla o alucina un nombre, tener un fallback o manejar el error
            print(f"Alerta: El enrutador sugirió un capitán inválido ('{captain_name}'). Usando un fallback.")
            # Un fallback simple podría ser un capitán general o el de documentación.
            return "Documentación y Formatos"

    def process_command(self, query: str) -> str:
        """
        Procesa un comando, lo enruta al capitán correcto y ejecuta la misión.
        """
        print(f"General de SG-SST: Orden recibida - '{query}'")

        # 1. Decidir qué capitán es el adecuado
        captain_name = self._route_to_captain(query)
        print(f"General de SG-SST: Orden enrutada al '{captain_name}'.")

        # 2. Delegar la tarea al capitán seleccionado
        selected_captain = self.captains[captain_name]
        response = selected_captain.run(query)

        print(f"General de SG-SST: Misión completada por '{captain_name}'. Respuesta final: {response}")
        return response
