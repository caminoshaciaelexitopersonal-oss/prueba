import os
import flet as ft
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_community.llms import LlamaCpp
from typing import Dict, Any, Union

# Singleton instance for the LLM
_llm_instance = None
_llm_status = "not_initialized"

def initialize_llm(page: ft.Page, config: Dict[str, Any]) -> None:
    """
    Initializes the LLM based on a dynamic configuration dictionary.
    Sets a global status that can be checked by the UI.
    """
    global _llm_instance, _llm_status
    if _llm_status != "not_initialized":
        return

    provider = config.get("llm_preference", "local")
    _llm_status = f"initializing_{provider}"
    print(f"--- 🧠 Inicializando LLM con proveedor: '{provider}' ---")

    llm = None
    if provider == "openai":
        api_key = config.get("openai_api_key")
        if not api_key:
            _llm_status = "error_openai_key_missing"
        else:
            llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0)

    elif provider == "google":
        api_key = config.get("google_api_key")
        if not api_key:
            _llm_status = "error_google_key_missing"
        else:
            llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-1.5-flash")

    elif provider == "local":
        platform = page.platform
        if platform in ["android", "ios"]:
            model_path = "assets/models/phi-1_5.gguf"
            if not os.path.exists(model_path):
                _llm_status = "error_local_model_missing"
            else:
                llm = LlamaCpp(model_path=model_path, n_ctx=2048, n_gpu_layers=0, verbose=False)
        else: # Desktop
            try:
                llm = ChatOllama(model="llama3")
                llm.invoke("test")
            except Exception:
                _llm_status = "error_ollama_not_found"
    else:
        _llm_status = "error_unknown_provider"

    if llm:
        _llm_instance = llm
        _llm_status = "initialized"
        print(f"--- ✅ LLM del proveedor '{provider}' inicializado correctamente. ---")

def get_llm_instance() -> Any:
    """Returns the singleton LLM instance."""
    return _llm_instance

def get_llm_status() -> str:
    """Returns the current status of the LLM initialization."""
    return _llm_status
