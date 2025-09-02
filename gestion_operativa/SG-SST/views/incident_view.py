import flet as ft
from .. import database

class IncidentView(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.incident_list = ft.ListView(expand=True, spacing=10)

        # The dropdown now uses dummy data to avoid the cross-system dependency.
        self.employee_dropdown = ft.Dropdown(
            label="Seleccionar Empleado (Datos de Prueba)",
            options=self.get_employee_options(),
            expand=True,
        )

    def did_mount(self):
        self.page.pubsub.subscribe(self.on_incident_update)
        self.refresh_incident_list()

    def will_unmount(self):
        self.page.pubsub.unsubscribe(self.on_incident_update)
        super().will_unmount()

    def on_incident_update(self, message):
        self.refresh_incident_list()

    def build(self):
        return ft.Column(
            controls=[
                ft.Row([ft.Text("Gestión de Incidentes", size=24, weight=ft.FontWeight.BOLD)]),
                ft.Text("La lista de incidentes se actualiza en tiempo real."),
                self.employee_dropdown, # Dropdown with dummy data
                ft.Divider(),
                ft.Container(
                    content=self.incident_list,
                    border=ft.border.all(1, ft.colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=True,
                ),
            ],
            expand=True,
        )

    def get_employee_options(self):
        """Returns dummy employee data for the dropdown."""
        print("Cargando empleados de prueba para el dropdown.")
        return [
            ft.dropdown.Option(key="1", text="Empleado de Prueba 1"),
            ft.dropdown.Option(key="2", text="Empleado de Prueba 2"),
        ]

    def refresh_incident_list(self):
        self.incident_list.controls.clear()
        try:
            incidents = database.list_incidents()
            if not incidents:
                self.incident_list.controls.append(ft.Text("No hay incidentes registrados."))
            else:
                for inc in incidents:
                    self.incident_list.controls.append(
                        ft.Text(f"[{inc.incident_date}] {inc.description[:50]}... (Severidad: {inc.severity})")
                    )
        except Exception as e:
            self.incident_list.controls.append(ft.Text(f"Error al cargar incidentes: {e}", color=ft.colors.RED))

        if self.page:
            self.update()
