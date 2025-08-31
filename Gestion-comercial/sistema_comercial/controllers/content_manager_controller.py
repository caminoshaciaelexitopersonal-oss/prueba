import flet as ft
import datetime
from models.content_model import ContentModel
from views.content_manager_view import ContentManagerView
from models.calendar_model import CalendarModel, ScheduledPost
from controllers.calendar_controller import CalendarController

class ContentManagerController:
    def __init__(self, model: ContentModel, view: ContentManagerView, calendar_model: CalendarModel, calendar_controller: CalendarController):
        self.model = model
        self.view = view
        self.calendar_model = calendar_model
        self.calendar_controller = calendar_controller
        self.page = None  # Will be populated when the view is on the page

        self.generated_content_for_scheduling = None

        # Connect handlers
        self.view.generate_text_button.on_click = self.generate_text_clicked
        self.view.generate_video_button.on_click = self.generate_video_script_clicked
        self.view.schedule_button.on_click = self.schedule_content_clicked

    async def generate_text_clicked(self, e):
        """Handles the click event for the 'Generate Text' button."""
        idea = self.view.text_idea_input.value
        if not idea:
            self.view.generated_text_area.value = "Por favor, introduce una idea para el post."
            await self.view.update_async()
            return

        self.view.generate_text_button.disabled = True
        self.view.schedule_button.disabled = True
        self.view.generated_text_area.value = "Generando texto... 🤖"
        await self.view.update_async()

        try:
            generated_text = await self.model.generate_post(idea)
            self.view.generated_text_area.value = generated_text
            self.generated_content_for_scheduling = {"type": "text", "content": generated_text}
            self.view.schedule_button.disabled = False
        except Exception as ex:
            self.view.generated_text_area.value = f"**Error:**\n\n{ex}"
        finally:
            self.view.generate_text_button.disabled = False
            await self.view.update_async()

    async def generate_video_script_clicked(self, e):
        """Handles the click event for the 'Generate Video Script' button."""
        idea = self.view.video_idea_input.value
        vid_format = self.view.video_format_dropdown.value
        duration = self.view.video_duration_input.value

        if not all([idea, vid_format, duration]):
            self.view.generated_video_area.value = "Por favor, rellena todos los campos para el video."
            await self.view.update_async()
            return

        self.view.generate_video_button.disabled = True
        self.view.schedule_button.disabled = True
        self.view.generated_video_area.value = "Generando guion... 🎥"
        await self.view.update_async()

        try:
            generated_script = await self.model.generate_video_script(idea, vid_format, duration)
            self.view.generated_video_area.value = generated_script
            self.generated_content_for_scheduling = {"type": "video", "script": generated_script, "format": vid_format, "duration": duration}
            self.view.schedule_button.disabled = False
        except Exception as ex:
            self.view.generated_video_area.value = f"**Error:**\n\n{ex}"
        finally:
            self.view.generate_video_button.disabled = False
            await self.view.update_async()

    async def schedule_content_clicked(self, e):
        """Opens a date picker to schedule the generated content."""
        if not self.generated_content_for_scheduling:
            return

        if not self.page:
            self.page = self.view.page

        async def on_date_picked(e_date):
            if e_date.control.value:
                selected_date = e_date.control.value.date()

                new_post = ScheduledPost(
                    date=selected_date,
                    content_type=self.generated_content_for_scheduling["type"],
                    content_data=self.generated_content_for_scheduling,
                )

                self.calendar_model.add_post(new_post)
                self.calendar_controller.update_calendar()

                self.page.snack_bar = ft.SnackBar(ft.Text(f"Contenido programado para el {selected_date.strftime('%d/%m/%Y')}."))
                self.page.snack_bar.open = True
                await self.page.update_async()

        date_picker = ft.DatePicker(
            on_change=on_date_picked,
            first_date=datetime.datetime.now() - datetime.timedelta(days=1),
            help_text="Selecciona una fecha para programar",
            cancel_text="Cancelar",
            confirm_text="Confirmar",
        )

        self.page.overlay.append(date_picker)
        await self.page.update_async()
        await date_picker.pick_date_async()
