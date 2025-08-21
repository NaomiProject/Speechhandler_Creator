from naomi.plugin import SpeechHandlerPlugin

class {PLUGIN_CLASS}(SpeechHandlerPlugin):
    def intents(self):
        return {
            "{PLUGIN_NAME}Intent": {
                "keywords": {KEYWORDS},
                "templates": {TEMPLATES}
            }
        }

    def handle(self, intent, mic):
        mic.say(f"You said: {intent.get('text', '')}")
