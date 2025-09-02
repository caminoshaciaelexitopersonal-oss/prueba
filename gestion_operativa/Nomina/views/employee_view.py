import flet as ft
import threading
import time
from agent.graph import HRAgent
import database # To get the list of employees

class EmployeeView(ft.UserControl):
    def __init__(self, agent: HRAgent):
        super().__init__(expand=True)
        self.agent = agent

        self.employee_list = ft.ListView(expand=True, spacing=10)
        self.refresh_button = ft.ElevatedButton("Refresh List", on_click=self.refresh_employee_list)

        self.chat_input = ft.TextField(
            hint_text="e.g., 'list all employees' or 'add employee Jane Doe, developer, 60000, 2023-01-15'",
            expand=True,
            on_submit=self.send_message_click,
        )
        self.send_button = ft.IconButton(icon=ft.icons.SEND, on_click=self.send_message_click)

        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        # Initial load of employees
        self.refresh_employee_list(None)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row([ft.Text("Employee Management", size=24, weight=ft.FontWeight.BOLD), self.refresh_button]),
                ft.Text("Use the chat below to manage employees with the AI agent."),
                ft.Divider(),
                ft.Container(
                    content=self.employee_list,
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

    def refresh_employee_list(self, e):
        self.employee_list.controls.clear()
        employees = database.list_employees()
        if not employees:
            self.employee_list.controls.append(ft.Text("No employees found."))
        else:
            for emp in employees:
                self.employee_list.controls.append(
                    ft.Text(f"{emp.name} - {emp.position} (ID: ...{str(emp.id)[-4:]})")
                )
        self.update()

    def send_message_click(self, e):
        user_input = self.chat_input.value
        if not user_input:
            return

        self.add_to_chat_history("You", user_input)
        self.chat_input.value = ""
        self.update()

        # Start agent invocation in a new thread
        thread = threading.Thread(target=self.run_agent, args=(user_input,))
        thread.start()

    def run_agent(self, user_input):
        agent_response_text = ft.Text("Agent is thinking...")
        self.page.run_threadsafe(self.add_control_to_chat, ("Agent", agent_response_text))

        response_content = ""
        try:
            for chunk in self.agent.invoke(user_input):
                last_message = chunk['messages'][-1]
                if last_message.content:
                    response_content = last_message.content

                self.page.run_threadsafe(self.update_agent_response, (agent_response_text, response_content))
                time.sleep(0.1)
        except Exception as e:
            self.page.run_threadsafe(self.update_agent_response, (agent_response_text, f"An error occurred: {e}"))

    def add_to_chat_history(self, user: str, message: str):
        self.chat_history.controls.append(
            ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), ft.Text(message, selectable=True)])
        )
        self.update()

    def add_control_to_chat(self, user: str, control: ft.Control):
        self.chat_history.controls.append(
             ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), control])
        )
        self.update()

    def update_agent_response(self, text_control, new_content):
        text_control.value = new_content
        self.update()
