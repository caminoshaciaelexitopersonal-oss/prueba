import flet as ft

def main(page: ft.Page):
    page.title = "SG-SST System"
    page.add(ft.Text("Welcome to the Safety and Health Management System!", size=24))
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
