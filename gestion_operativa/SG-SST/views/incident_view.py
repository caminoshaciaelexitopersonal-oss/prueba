# gestion_operativa/SG-SST/views/incident_view.py
import flet as ft
from gestion_operativa.SG_SST import database

class IncidentView(ft.UserControl):
    """
    A clean, simple view to display a list of reported safety incidents.
    """
    def __init__(self):
        super().__init__(expand=True)
        self.incident_list = ft.ListView(expand=True, spacing=10)
        self.refresh_button = ft.ElevatedButton("Refrescar Lista", on_click=self.refresh_incident_list)

    def did_mount(self):
        self.refresh_incident_list(None)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Incidentes Reportados", size=20, weight=ft.FontWeight.BOLD),
                        self.refresh_button
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Container(
                    content=self.incident_list,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=True,
                ),
            ],
            expand=True,
        )

    def refresh_incident_list(self, e):
        self.incident_list.controls.clear()
        try:
            incidents = database.list_incidents()
            if not incidents:
                self.incident_list.controls.append(ft.Text("No se han reportado incidentes."))
            else:
                for inc in incidents:
                    self.incident_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED),
                            title=ft.Text(f"{inc.description[:60]}..."),
                            subtitle=ft.Text(f"Lugar: {inc.location} | Fecha: {inc.incident_date} | Severidad: {inc.severity}")
                        )
                    )
        except Exception as ex:
            self.incident_list.controls.append(ft.Text(f"Error al cargar incidentes: {ex}"))
        self.update()
