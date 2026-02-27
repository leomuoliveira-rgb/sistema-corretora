import flet as ft

def main(page: ft.Page):
    page.title = "Test Tabs"

    # Testar sintaxe de Tab
    tabs = ft.Tabs(
        tabs=[
            ft.Tab(
                content=ft.Text("Tab 1 content"),
            ),
        ]
    )

    page.add(tabs)

ft.app(target=main)
