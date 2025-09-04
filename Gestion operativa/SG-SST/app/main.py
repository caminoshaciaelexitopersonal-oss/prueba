import flet as ft
import threading
import time
from agents.graph import app as agent_app

# A simple in-memory store for our inspections, acting as a simulated database.
inspections_db = []

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Seguridad y Salud en el Trabajo (SG-SST)"
    page.window_width = 800
    page.window_height = 600

    # --- UI Controls ---

    # ListView to display the list of inspections
    inspections_list_view = ft.ListView(expand=True, spacing=10)

    def update_inspections_list():
        """Re-renders the list of inspections from the in-memory db."""
        inspections_list_view.controls.clear()
        if not inspections_db:
            inspections_list_view.controls.append(ft.Text("No hay inspecciones registradas."))
        else:
            for insp in inspections_db:
                inspections_list_view.controls.append(
                    ft.Container(
                        content=ft.Text(insp),
                        bgcolor=ft.colors.BLUE_GREY_50,
                        padding=10,
                        border_radius=5
                    )
                )
        page.update()

    # Text field for entering commands (simulates voice input)
    command_input = ft.TextField(
        label="Escriba una orden para el General...",
        expand=True,
        on_submit=lambda e: send_command(e.control.value)
    )

    # Progress indicator
    progress_ring = ft.ProgressRing(visible=False)

    # Agent response text
    response_text = ft.Text("", italic=True)

    # --- Agent Execution Logic ---

    def run_agent_in_thread(command: str):
        """Runs the agent graph in a separate thread to avoid blocking the UI."""

        # Show progress ring and disable input
        progress_ring.visible = True
        command_input.disabled = True
        page.update()

        try:
            # The final result of the graph stream is the last message.
            final_response = {}
            for output in agent_app.stream({"command": command}):
                # We are interested in the final state of the subgraph
                for key, value in output.items():
                    if key == "inspecciones_seguridad":
                        final_response = value

            # Update UI based on agent's action
            # This is a simple simulation of the agent's effect.
            # A real implementation would have the tactical agent modify a real DB.
            response_message = final_response.get("response", "Acción completada sin respuesta detallada.")
            if "creada" in response_message:
                # The agent created something, so we add it to our simulated DB
                # and update the list.
                inspections_db.append(response_message)
                update_inspections_list()

            response_text.value = f"Respuesta del Agente: {response_message}"

        except Exception as e:
            response_text.value = f"Error al ejecutar el agente: {e}"
        finally:
            # Hide progress ring and re-enable input
            progress_ring.visible = False
            command_input.disabled = False
            page.update()

    def send_command(command: str):
        """Kicks off the agent thread."""
        if not command:
            return

        response_text.value = f"Orden enviada: '{command}'"
        command_input.value = ""

        # Run the agent in a background thread
        thread = threading.Thread(target=run_agent_in_thread, args=(command,))
        thread.start()


    # --- Page Layout ---

    page.add(
        ft.Column(
            [
                ft.Text("Módulo de Inspecciones", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row([command_input, ft.ElevatedButton("Enviar Orden", on_click=lambda e: send_command(command_input.value))]),
                ft.Row([progress_ring, response_text]),
                ft.Divider(),
                ft.Text("Inspecciones Registradas:", style=ft.TextThemeStyle.TITLE_MEDIUM),
                inspections_list_view
            ],
            expand=True
        )
    )

    # Initial render of the list
    update_inspections_list()


if __name__ == "__main__":
    ft.app(target=main)
