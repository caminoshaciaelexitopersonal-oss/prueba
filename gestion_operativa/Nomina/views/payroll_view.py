import flet as ft
import threading
from agent.graph import HRAgent
import database

class PayrollView(ft.UserControl):
    def __init__(self, agent: HRAgent):
        super().__init__(expand=True)
        self.agent = agent

        self.employee_dropdown = ft.Dropdown(
            label="Select Employee",
            hint_text="Choose an employee to calculate payroll",
            options=self.get_employee_options(),
            expand=True,
        )

        self.calculate_button = ft.ElevatedButton(
            "Generate Payslip",
            on_click=self.generate_payslip_click,
            icon=ft.icons.CALCULATE
        )

        self.payslip_display = ft.Markdown(
            "Select an employee and click 'Generate Payslip' to see the details here.",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        )

    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Payroll Calculation", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[self.employee_dropdown, self.calculate_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Container(
                    content=self.payslip_display,
                    padding=ft.padding.all(10),
                    expand=True
                )
            ],
            expand=True,
        )

    def get_employee_options(self):
        employees = database.list_employees()
        return [ft.dropdown.Option(key=str(emp.id), text=emp.name) for emp in employees]

    def generate_payslip_click(self, e):
        employee_id = self.employee_dropdown.value
        if not employee_id:
            # You could show an error in a snackbar, etc.
            return

        employee = database.get_employee(employee_id)
        if not employee:
            return

        self.payslip_display.value = "Agent is calculating..."
        self.update()

        # A more complex prompt could be constructed to use all tools.
        # For now, we'll ask for a summary based on one tool.
        prompt = f"Calculate the social security contributions for a salary of {employee.salary}"

        thread = threading.Thread(target=self.run_agent, args=(prompt,))
        thread.start()

    def run_agent(self, prompt):
        response_content = ""
        try:
            for chunk in self.agent.invoke(prompt):
                last_message = chunk['messages'][-1]
                if last_message.content:
                    response_content = last_message.content
        except Exception as e:
            response_content = f"An error occurred: {e}"

        # Format the response nicely for the markdown display
        formatted_response = f"## Payslip Details\n\n```json\n{response_content}\n```"
        self.page.run_threadsafe(self.update_payslip_display, (formatted_response,))

    def update_payslip_display(self, content):
        self.payslip_display.value = content
        self.update()
