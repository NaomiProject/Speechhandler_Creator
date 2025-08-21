import os
from pathlib import Path
from utils import load_template, save_file

def generate_plugin(name, description, license, keywords, templates, output_dir):
    class_name = ''.join(word.capitalize() for word in name.split())
    folder_path = Path(output_dir) / name
    folder_path.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_code = load_template("templates/plugin_init_template.py").format(
        PLUGIN_CLASS=class_name,
        PLUGIN_NAME=name.lower(),
        KEYWORDS=keywords,
        TEMPLATES=templates
    )
    save_file(folder_path / "__init__.py", init_code)

    # Create plugin.info
    plugin_info = load_template("templates/plugin_info_template.txt").format(
        PLUGIN_NAME=name,
        DESCRIPTION=description,
        LICENSE=license,
        PLUGIN_URL="https://github.com/yourusername/" + name
    )
    save_file(folder_path / "plugin.info", plugin_info)

    # Create README.md
    save_file(folder_path / "README.md", f"# {name}\n\n{description}")

    return folder_path

def create_plugin_skeleton(name, description, license_name, keywords):
    folder = name.replace(" ", "_")
    os.makedirs(folder, exist_ok=True)

    # Create plugin.info
    with open(os.path.join(folder, "plugin.info"), "w") as f:
        f.write(f"name={name}\n")
        f.write(f"description={description.strip()}\n")
        f.write(f"license={license_name}\n")
        f.write(f"keywords={','.join(keywords)}\n")

    # Create __init__.py
    with open(os.path.join(folder, "__init__.py"), "w") as f:
        f.write("# Naomi speechhandler plugin\n")

    # Create main handler file
    handler_name = name.replace(" ", "") + "Handler.py"
    with open(os.path.join(folder, handler_name), "w") as f:
        f.write(f'''from naomi import plugin

class {name.replace(" ", "")}Handler(plugin.SpeechHandlerPlugin):
    def intents(self):
        return {{
            "RepeatIntent": {{
                "keywords": {keywords}
            }}
        }}

    def handle(self, text, intent):
        self.say(text)
''')

