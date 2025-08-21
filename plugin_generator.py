# plugin_generator.py
import os

def create_plugin_skeleton(name, description, license_name, keywords):
    folder = name.replace(" ", "_")
    os.makedirs(folder, exist_ok=True)

    # plugin.info
    with open(os.path.join(folder, "plugin.info"), "w", encoding="utf-8") as f:
        f.write(f"name={name}\n")
        f.write(f"description={description}\n")
        f.write(f"license={license_name}\n")
        f.write(f"keywords={','.join(keywords)}\n")

    # __init__.py
    with open(os.path.join(folder, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Naomi speechhandler plugin\n")

    # Handler file
    handler_filename = name.replace(" ", "") + "Handler.py"
    with open(os.path.join(folder, handler_filename), "w", encoding="utf-8") as f:
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
