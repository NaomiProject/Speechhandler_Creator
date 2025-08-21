import tkinter as tk
from tkinter import messagebox, scrolledtext
from plugin_generator import create_plugin_skeleton

def run():
    root = tk.Tk()
    root.title("Naomi Plugin Creator")

    # Plugin metadata
    tk.Label(root, text="Plugin Name").grid(row=0, column=0, sticky="w")
    entry_name = tk.Entry(root, width=40)
    entry_name.grid(row=0, column=1, pady=2)

    tk.Label(root, text="Description").grid(row=1, column=0, sticky="nw")
    text_desc = scrolledtext.ScrolledText(root, width=30, height=3)
    text_desc.grid(row=1, column=1, pady=2)

    tk.Label(root, text="License").grid(row=2, column=0, sticky="w")
    entry_license = tk.Entry(root, width=40); entry_license.insert(0, "MIT")
    entry_license.grid(row=2, column=1, pady=2)

    # Intent input
    intents_frame = tk.Frame(root)
    intents_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

    tk.Label(intents_frame, text="Intents:").grid(row=0, column=0, sticky="w")

    intent_rows = []

    def add_intent_row():
        idx = len(intent_rows)
        name_entry = tk.Entry(intents_frame, width=20)
        templates_entry = tk.Entry(intents_frame, width=30)
        keywords_entry = tk.Entry(intents_frame, width=30)
        name_entry.grid(row=idx+1, column=0, padx=5, pady=2)
        templates_entry.grid(row=idx+1, column=1, padx=5)
        keywords_entry.grid(row=idx+1, column=2, padx=5)
        intent_rows.append((name_entry, templates_entry, keywords_entry))

    tk.Button(root, text="Add Intent", command=add_intent_row).grid(row=4, column=0)
    add_intent_row()  # one row to start

    def on_create():
        name = entry_name.get().strip()
        description = text_desc.get("1.0", tk.END).strip()
        license_name = entry_license.get().strip()
        intent_data = []
        for name_e, temp_e, key_e in intent_rows:
            intent_name = name_e.get().strip()
            if not intent_name:
                continue
            templates = [t.strip() for t in temp_e.get().split(",") if t.strip()]
            keywords = [k.strip() for k in key_e.get().split(",") if k.strip()]
            intent_data.append({
                "intent_name": intent_name,
                "templates": templates,
                "keywords": keywords
            })

        if not name or not intent_data:
            messagebox.showerror("Error", "Plugin name and at least one intent required.")
            return

        create_plugin_skeleton(name, description, license_name, intent_data)
        messagebox.showinfo("Success", f"Plugin '{name}' created!")

    tk.Button(root, text="Create Plugin", command=on_create).grid(row=5, column=0, pady=10)
    tk.Button(root, text="Exit", command=root.destroy).grid(row=5, column=1)

    root.mainloop()
