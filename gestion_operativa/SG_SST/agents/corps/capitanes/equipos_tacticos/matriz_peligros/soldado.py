import flet as ft
import uuid
from gestion_operativa.SG_SST import database
from gestion_operativa.SG_SST.models.risk import Risk

class SoldadoMatrizPeligros:
    def __init__(self, page: ft.Page):
        self.page = page
        print("Soldado de Matriz de Peligros: ¡Listo y dispuesto!")

    def ejecutar_accion(self, accion: str) -> str:
        """
        Ejecuta la acción final: interactúa con la base de datos y notifica a la UI.
        Ejemplo de 'accion': "Añadir riesgo: 'Caída de objetos', Área: 'Almacén', Nivel: 'Alto'"
        """
        print(f"Soldado: ¡Ejecutando acción! - '{accion}'")

        try:
            # --- 1. Parsear la acción (lógica simple para el ejemplo) ---
            # En un caso real, la información vendría más estructurada.
            parts = {p.split(':')[0].strip(): p.split(':')[1].strip().strip("'") for p in accion.split(', ')}
            risk_name = parts.get("Añadir riesgo", "Riesgo Desconocido")
            area = parts.get("Área", "Área Desconocida")
            level = parts.get("Nivel", "Bajo")

            # --- 2. Crear el objeto Risk ---
            new_risk = Risk(
                name=risk_name,
                description=f"Riesgo de '{risk_name}' en el área de '{area}'.",
                area=area,
                risk_level=level,
                controls=["Señalización", "EPP"] # Controles de ejemplo
            )

            # --- 3. Interactuar con la base de datos ---
            database.add_risk(new_risk)
            print(f"Soldado: Riesgo '{new_risk.name}' añadido a la base de datos.")

            # --- 4. Notificar a la UI para que se actualice ---
            if self.page and self.page.pubsub:
                self.page.pubsub.send_all(message="risk_update")
                print("Soldado: Notificación enviada a la UI para refrescar.")

            return "Soldado: ¡Objetivo cumplido! Base de datos actualizada y UI notificada."

        except Exception as e:
            print(f"Soldado: Error durante la ejecución de la acción: {e}")
            return f"Soldado: Falló la misión. Error: {e}"
