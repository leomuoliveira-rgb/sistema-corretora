import flet as ft
from main import main

ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,
    host="0.0.0.0",
    port=8550,
)
