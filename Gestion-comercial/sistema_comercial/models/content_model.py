import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class ContentModel:
    def __init__(self):
        # We will check for the API key when generating content.
        # This allows the app to start even if the key is not yet set.
        self.llm = None
        self.chain = None

        # Define the prompt template for generating social media posts
        self.text_post_prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en marketing y redes sociales. Tu tarea es crear publicaciones atractivas y profesionales."),
            ("user", "Por favor, crea una publicación para redes sociales (adecuada para Instagram o Facebook) basada en la siguiente idea: {idea}")
        ])

        # Define the prompt template for generating video scripts
        self.video_script_prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un guionista experto en crear contenido viral para redes sociales. Tu tarea es crear un guion detallado para un video corto."),
            ("user", "Por favor, crea un guion para un video de {duration} segundos en formato {vid_format}. El guion debe estar basado en la siguiente idea: {idea}. Estructura el guion escena por escena, describiendo la acción visual y el diálogo o texto en pantalla.")
        ])

    def _initialize_chain(self):
        """Initializes the LangChain chains, checking for the API key."""
        if self.llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada. Por favor, añádela a un archivo .env en la raíz del proyecto.")

            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
            self.text_post_chain = self.text_post_prompt | self.llm | StrOutputParser()
            self.video_script_chain = self.video_script_prompt | self.llm | StrOutputParser()

    async def generate_post(self, idea: str) -> str:
        """Generates a social media post using LangChain."""
        try:
            self._initialize_chain()
            response = await self.text_post_chain.ainvoke({"idea": idea})
            return response
        except Exception as e:
            return f"Error al generar contenido: {e}"

    async def generate_video_script(self, idea: str, vid_format: str, duration: str) -> str:
        """Generates a video script using LangChain."""
        try:
            self._initialize_chain()
            response = await self.video_script_chain.ainvoke({
                "idea": idea,
                "vid_format": vid_format,
                "duration": duration
            })
            return response
        except Exception as e:
            return f"Error al generar el guion del video: {e}"
