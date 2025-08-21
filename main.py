# gui.py
import PySimpleGUI as sg
from plugin_generator import create_plugin_skeleton

def run():
    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("Naomi Plugin Creator", font=("Helvetica", 16))],
        [sg.Text("Plugin Name"), sg.Input(key="name")],
        [sg.Text("Description"), sg.Multiline(size=(40, 4), key="description")],
        [sg.Text("License"), sg.Input(key="license", default_text="MIT")],
        [sg.Text("Intent Keywords (comma-separated)"), sg.Input(key="keywords")],
        [sg.Button("Create Plugin"), sg.Button("Exit")]
    ]

    window = sg.Window("Naomi Plugin Creator", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        elif event == "Create Plugin":
            create_plugin_skeleton(
                name=values["name"],
                description=values["description"],
                license_name=values["license"],
                keywords=[kw.strip() for kw in values["keywords"].split(",") if kw.strip()]
            )
            sg.popup("Plugin created successfully!")

    window.close()
