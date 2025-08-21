import os
from pathlib import Path
from utils import save_file

TEMPLATE_INFO = """[plugin]
name={name}
description={description}
license={license}
type=speechhandler
version=0.0.1
"""

TEMPLATE_INIT = '''from naomi.plugin import SpeechHandlerPlugin

class {class_name}(SpeechHandlerPlugin):
    def intents(self):
        return {intents_dict}

    def handle(self, intent, mic):
        mic.say(intent.get('text', ''))
'''

def create_plugin_skeleton(name, description, license_name, intent_data):
    folder = name.replace(" ", "_")
    os.makedirs(folder, exist_ok=True)

    # plugin.info
    info = TEMPLATE_INFO.format(name=name, description=description, license=license_name)
    save_file(Path(folder) / "plugin.info", info)

    # Build intents dict
    intents = {}
    for intent in intent_data:
        intents[intent["intent_name"]] = {
            "locale": {
                "en-US": {
                    "templates": intent["templates"],
                    "keywords": intent["keywords"]
                }
            },
            "action": "self.handle"
        }

    # render __init__.py
    class_name = name.replace(" ", "") + "Handler"
    init_code = TEMPLATE_INIT.format(
        class_name=class_name,
        intents_dict=intents
    )
    save_file(Path(folder) / "__init__.py", init_code)

    # README
    readme = f"# {name}\n\n{description}\n"
    save_file(Path(folder) / "README.md", readme)

    return folder
