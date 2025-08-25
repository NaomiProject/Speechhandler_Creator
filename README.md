# Speechhandler_Creator
A vibe-coding project with ChatGPT - an editor for creating speechhandler plugins

The **Speechhandler_Creator** is a graphical tool for building and publishing speechhandler plugins for the [Naomi voice assistant](https://github.com/NaomiProject/Naomi).

It simplifies the entire process of:
- Defining **intents** (keywords + templates) for your plugin
- Generating a Python `SpeechHandler` plugin template
- Publishing your plugin to GitHub
- Submitting a pull request to the [Naomi Plugin Exchange](https://github.com/NaomiProject/naomi-plugins)

This tool helps developers jump straight into writing plugin logic without worrying about boilerplate setup.

---

## Installation

Clone this repository:

```bash
git clone https://github.com/NaomiProject/naomi-plugin-creator.git
cd naomi-plugin-creator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.9+
- [tkinter](https://docs.python.org/3/library/tkinter.html) (usually comes with Python)
- [PyGithub](https://pygithub.readthedocs.io/en/latest/)
- A GitHub account with a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (classic, repo scope)

---

## Running the Tool

Start the application:

```bash
python main.py
```

The Plugin Creator window will open with tabs for:
- **General Info** – name, description, license, repo URL
- **Intents** – define keywords and templates
- **Locales** – manage multiple language variants
- **Publish** – push your plugin to GitHub and the Naomi registry

---

## Creating a Plugin (Example: Weather Report)

Let’s create a plugin called `WeatherPlugin`.

### Step 1: General Info
- **Name**: `WeatherPlugin`
- **Description**: "Provides local weather forecasts."
- **License**: `MIT`
- **Repo URL**: leave blank to let the tool create a GitHub repo for you.

### Step 2: Add Intents
Think of how you might expect a user to interact with your plugin. For the weather plugin, the user might use phrases such as:
* What is the forecast?
* Will it be windy this afternoon?
* When is it going to rain in Cincinnati?

Obviously, you don't want to have to enter every possible way that a user might interact with your plugin, but you can break down the phrases into templates and keywords. An additional benefit of this is that Naomi will return the user's request to your plugin with the keywords split out already so your plugin does not have to parse the user's input directly. Keywords found in user input can be picked up from the "intent['matches']" key in the "intent" object received by the "handle" method.

An "intent" for Naomi is basically asking for a particular program to be run. Each intent can be sent to a different handler function, or you can have one handler function for your intent that performs different functions depending on the value of "intent['intent']".

To add an intent, click the "Add" button next to the "intents" area. Give your intent a name, then a brief description to help users know what your plugin does.

#### Step 2A: Add Keywords
Add keywords so Naomi can extract values from user input.

Click the "Add" button next to "Keyword Categories".
Give your keyword a descriptive name and add a comma separated list of possible values.

Example keywords output:
```json
{
  "ForecastKeyword": ["forecast", "outlook"],
  "WeatherConditionKeyword": ["rain", "snow", "be windy", "be sunny"],
  "DayKeyword": ["today", "tomorrow", "Monday", "this"],
  "TimeOfDayKeyword": ["morning", "afternoon", "evening", "night"],
  "LocationKeyword": ["Cincinnati", "New York", "Chicago"]
}
```

#### Step 2B: Add Templates
Templates show how keywords fit into natural phrases.

Example templates:
- `"What is the {ForecastKeyword}?"`
- `"Will it {WeatherConditionKeyword} {DayKeyword} {TimeOfDayKeyword}?"`
- `"When is it going to {WeatherConditionKeyword} in {LocationKeyword}?"`

Use curly brackets to denote that the intent parser should expect a keyword from a keyword list in that location.

### Step 3: Generate Plugin
Click **Generate Plugin**

This creates:
```
WeatherPlugin/
  ├── __init__.py        # plugin template
  ├── plugin.info
  ├── README.md
```

The starter plugin simply repeats back the detected intent for debugging. To test your plugin, copy the whole directory to one of the Naomi speechhandler plugins directories - either ~/Naomi/plugins/speechhander or ~/.config/naomi/plugins/speechhandler - and re-start Naomi. Watch for any error messages saying that your plugin has been skipped. Try triggering your plugin by saying some of the phrases you designed for it.

### Step 4: Implement Your Logic
Open `__init__.py` in your favorite editor and replace the handler logic with real API calls.

### Step 5: Publish
When ready:
1. Re-open the Plugin Creator
2. Go to the **Publish** tab
3. Select your plugin project
4. Enter your [GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
5. Click **Publish**

The tool will:
- Commit any changes
- Push to your GitHub repo
- Create a pull request to add your plugin to the Naomi registry

---
## Troubleshooting

One particularly vexing issue was trying to publish an update when the "master" branch of my forked copy of the naomi-plugins repository had diverged from the "master" branch of the main repository. This was causing the final pull request to fail. After trying a few things, I ended up simply deleting my forked copy and re-forking it fresh, which was okay because there really wasn't anything in there that I was worried about losing. In the years since I first forked that repository, I have learned the value of always creating a new branch for my changes so I can keep the master/main branch synchronized with upstream.

If you run into other issues with this program, please open an issue on the Github repository.

---

## Contributing

Pull requests are welcome!
See [Naomi Project](https://github.com/NaomiProject/Naomi) for full developer documentation.

---

## License

MIT License (same as the Naomi project).
