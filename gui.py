import PySimpleGUI as sg
from plugin_generator import generate_plugin
from publisher import publish_plugin

def start_gui():
    sg.theme("DarkBlue3")

    tab1_layout = [
        [sg.Text("Plugin Name"), sg.Input(key="-NAME-")],
        [sg.Text("Description"), sg.Input(key="-DESC-")],
        [sg.Text("License"), sg.Input(key="-LICENSE-")],
        [sg.Text("Keywords (comma-separated)"), sg.Input(key="-KEYWORDS-")],
        [sg.Text("Templates (comma-separated)"), sg.Input(key="-TEMPLATES-")],
        [sg.Text("Output Directory"), sg.Input(key="-OUTDIR-"), sg.FolderBrowse()],
        [sg.Button("Generate Plugin")]
    ]

    tab2_layout = [
        [sg.Text("Plugin Folder"), sg.Input(key="-PLUGINPATH-"), sg.FolderBrowse()],
        [sg.Text("GitHub Username"), sg.Input(key="-GHUSER-")],
        [sg.Text("GitHub Token"), sg.Input(key="-GHTOKEN-", password_char="*")],
        [sg.Button("Publish Plugin")]
    ]

    layout = [[sg.TabGroup([
        [sg.Tab("Create Plugin", tab1_layout), sg.Tab("Publish Plugin", tab2_layout)]
    ])]]

    window = sg.Window("Naomi Plugin Tool", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == "Generate Plugin":
            path = generate_plugin(
                values["-NAME-"],
                values["-DESC-"],
                values["-LICENSE-"],
                values["-KEYWORDS-"].split(","),
                values["-TEMPLATES-"].split(","),
                values["-OUTDIR-"]
            )
            sg.popup("Plugin created!", f"Path: {path}")

        if event == "Publish Plugin":
            url = publish_plugin(
                values["-PLUGINPATH-"],
                values["-GHUSER-"],
                values["-GHTOKEN-"]
            )
            sg.popup("Plugin published!", f"Pull Request URL: {url}")

    window.close()
