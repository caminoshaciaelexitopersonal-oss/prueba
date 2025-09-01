import flet as ft
import datetime
import calendar
from models.calendar_model import CalendarModel
from views.calendar_view import CalendarView

class CalendarController:
    def __init__(self, model: CalendarModel, view: CalendarView):
        self.model = model
        self.view = view
        self.current_date = datetime.date.today()

        # Connect handlers
        self.view.prev_month_button.on_click = self.prev_month
        self.view.next_month_button.on_click = self.next_month

        # Initial render
        self.update_calendar()

    def update_calendar(self):
        """Renders the calendar for the current month and year."""
        year = self.current_date.year
        month = self.current_date.month

        # Update header (Spanish locale)
        # Note: Flet doesn't have built-in localization, so this is a simple approach.
        month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.view.month_year_label.value = f"{month_names[month-1]} {year}"

        posts_by_day = self.model.get_posts_for_month(year, month)
        self.view.calendar_grid.controls.clear()

        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            for day in week:
                if day == 0:
                    self.view.calendar_grid.controls.append(ft.Container())
                else:
                    is_today = (year == datetime.date.today().year and month == datetime.date.today().month and day == datetime.date.today().day)

                    day_content = [ft.Text(str(day), weight=ft.FontWeight.BOLD)]
                    if day in posts_by_day:
                        for post in posts_by_day[day]:
                            icon = ft.icons.TEXT_FIELDS if post.content_type == 'text' else ft.icons.VIDEOCAM
                            day_content.append(ft.Icon(name=icon, size=16, color=ft.Colors.SECONDARY))

                    self.view.calendar_grid.controls.append(
                        ft.Container(
                            content=ft.Column(day_content, spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            border=ft.border.all(2, ft.Colors.SECONDARY) if is_today else ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=8,
                            padding=8,
                            alignment=ft.alignment.top_center,
                        )
                    )
        self.view.update()

    def prev_month(self, e):
        """Moves to the previous month and re-renders."""
        self.current_date = (self.current_date.replace(day=1) - datetime.timedelta(days=1))
        self.update_calendar()

    def next_month(self, e):
        """Moves to the next month and re-renders."""
        # This logic correctly handles moving to the next month across year boundaries
        self.current_date = (self.current_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        self.update_calendar()
