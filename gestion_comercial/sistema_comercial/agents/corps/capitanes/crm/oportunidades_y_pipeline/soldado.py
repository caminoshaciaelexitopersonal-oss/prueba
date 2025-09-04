import flet as ft
from gestion_comercial.sistema_comercial.agent.tools import add_new_lead, update_lead_status_tool

class SoldadoOportunidadesYPipeline:
    def __init__(self, page: ft.Page):
        self.page = page
        print("Soldado de Oportunidades y Pipeline: ¡Listo y dispuesto!")

    def ejecutar_accion(self, accion: str) -> str:
        """
        Ejecuta la acción final: llama a las herramientas para gestionar oportunidades.
        Ej: "command='add', customer_id='some-uuid', source='website', estimated_value=5000"
        Ej: "command='update', lead_id='another-uuid', new_status='contactado', new_pipeline_stage='negociacion'"
        """
        print(f"Soldado: ¡Ejecutando acción de pipeline! - '{accion}'")

        try:
            parts = accion.split(", ")
            command = parts[0].split("=")[1].strip("'")

            args = {}
            for part in parts[1:]:
                key, value = part.split("=")
                args[key.strip()] = value.strip("'")

            if command == 'add':
                # Convertir tipo de dato para el valor
                if 'estimated_value' in args:
                    args['estimated_value'] = float(args['estimated_value'])
                resultado = add_new_lead.invoke(args)
            elif command == 'update':
                resultado = update_lead_status_tool.invoke(args)
            else:
                resultado = "Error: Comando desconocido para este soldado. Use 'add' o 'update'."

            print(f"Soldado: Herramienta de pipeline ejecutada.")
            return f"Soldado: ¡Objetivo cumplido! {resultado}"

        except Exception as e:
            error_message = f"Soldado: Falló la misión. Error al procesar la acción '{accion}'. Detalle: {e}"
            print(error_message)
            return error_message
