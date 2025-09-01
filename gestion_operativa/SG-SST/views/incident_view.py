import flet as ft
import threading
import time
from agent.graph import SgsstAgent
import database
# We need to get the list of employees from the HR system's DB functions
# This is a bit of a hack. A better solution would be a shared data access layer.
import sys
sys.path.append('..') # Add the parent directory to the path
from hr_payroll_system.database import list_employees as list_all_employees

class IncidentView(ft.UserControl):
    def __init__(self, agent: SgsstAgent):
        super().__init__(expand=True)
        self.agent = agent

        self.incident_list = ft.ListView(expand=True, spacing=10)
        self.refresh_button = ft.ElevatedButton("Refresh List", on_click=self.refresh_incident_list)

        self.employee_dropdown = ft.Dropdown(
            label="Select Employee for Report",
            options=self.get_employee_options(),
            expand=True,
        )

        self.chat_input = ft.TextField(
            hint_text="e.g., 'report incident at warehouse, a box fell, date 2024-05-20'",
            expand=True,
            on_submit=self.send_message_click,
        )
        self.send_button = ft.IconButton(icon=ft.icons.SEND, on_click=self.send_message_click)

        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        self.refresh_incident_list(None)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row([ft.Text("Incident Management", size=24, weight=ft.FontWeight.BOLD), self.refresh_button]),
                ft.Text("Use the chat below to report and view incidents."),
                self.employee_dropdown,
                ft.Divider(),
                ft.Container(
                    content=self.incident_list,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=4,
                ),
                ft.Divider(),
                ft.Container(
                    content=self.chat_history,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=2,
                ),
                ft.Row(
                    controls=[self.chat_input, self.send_button],
                ),
            ],
            expand=True,
        )

    def get_employee_options(self):
        try:
            employees = list_all_employees()
            return [ft.dropdown.Option(key=str(emp.id), text=emp.name) for emp in employees]
        except Exception as e:
            print(f"Could not load employees for dropdown: {e}")
            return [ft.dropdown.Option(key="error", text="Could not load employees")]

    def refresh_incident_list(self, e):
        self.incident_list.controls.clear()
        incidents = database.list_incidents()
        if not incidents:
            self.incident_list.controls.append(ft.Text("No incidents found."))
        else:
            for inc in incidents:
                self.incident_list.controls.append(
                    ft.Text(f"[{inc.incident_date}] {inc.description[:50]}... (Severity: {inc.severity})")
                )
        self.update()

    def send_message_click(self, e):
        user_input = self.chat_input.value
        employee_id = self.employee_dropdown.value
        if not user_input or not employee_id or employee_id == "error":
            return

        self.add_to_chat_history("You", user_input)
        self.chat_input.value = ""
        self.update()

        # The agent needs the employee_id, but we can let it infer the other args
        full_prompt = f"For employee {employee_id}, {user_input}"

        thread = threading.Thread(target=self.run_agent, args=(full_prompt,))
        thread.start()

    def run_agent(self, prompt):
        agent_response_text = ft.Text("Agent is thinking...")
        self.page.run_threadsafe(self.add_control_to_chat, ("Agent", agent_response_text))

        response_content = ""
        try:
            for chunk in self.agent.invoke(prompt):
                last_message = chunk['messages'][-1]
                if last_message.content:
                    response_content = last_message.content
                self.page.run_threadsafe(self.update_agent_response, (agent_response_text, response_content))
                time.sleep(0.1)
        except Exception as e:
            self.page.run_threadsafe(self.update_agent_response, (agent_response_text, f"An error occurred: {e}"))

    def add_to_chat_history(self, user, message):
        self.chat_history.controls.append(
            ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), ft.Text(message, selectable=True)])
        )
        self.update()

    def add_control_to_chat(self, user, control):
        self.chat_history.controls.append(
             ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), control])
        )
        self.update()

    def update_agent_response(self, text_control, new_content):
        text_control.value = new_content
        self.update()
