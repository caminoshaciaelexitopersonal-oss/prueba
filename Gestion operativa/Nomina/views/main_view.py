import flet as ft
from .employee_view import EmployeeView
from .payroll_view import PayrollView
from agent.graph import HRAgent

class MainView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)

        self.agent = HRAgent()
        self.employee_view = EmployeeView(agent=self.agent)
        self.payroll_view = PayrollView(agent=self.agent)

        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.PERSON_SEARCH,
                    selected_icon=ft.icons.PERSON_SEARCH_OUTLINED,
                    label="Employees",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PAYMENT,
                    selected_icon=ft.icons.PAYMENT_OUTLINED,
                    label="Payroll",
                ),
            ],
            on_change=self.nav_change,
        )

        self.content_area = ft.Container(
            content=self.employee_view,
            expand=True,
            padding=ft.padding.all(20),
        )

    def build(self):
        return ft.Row(
            controls=[
                self.navigation_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.employee_view
        elif index == 1:
            self.content_area.content = self.payroll_view
        self.update()
