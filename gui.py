# gui.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
from plugin_generator import create_plugin_skeleton

def run():
    root = tk.Tk()
    root.title("Naomi Plugin Creator")

    # Title
    tk.Label(root, text="Naomi Plugin Creator", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Plugin Name
    tk.Label(root, text="Plugin Name").grid(row=1, column=0, sticky="w")
    entry_name = tk.Entry(root, width=40)
    entry_name.grid(row=1, column=1, pady=2)

    # Description
    tk.Label(root, text="Description").grid(row=2, column=0, sticky="nw")
    text_desc = scrolledtext.ScrolledText(root, width=30, height=4)
    text_desc.grid(row=2, column=1, pady=2)

    # License
    tk.Label(root, text="License").grid(row=3, column=0, sticky="w")
    entry_license = tk.Entry(root, width=40)
    entry_license.insert(0, "MIT")
    entry_license.grid(row=3, column=1, pady=2)

    # Keywords
    tk.Label(root, text="Intent Keywords (comma-separated)").grid(row=4, column=0, sticky="w")
    entry_keywords = tk.Entry(root, width=40)
    entry_keywords.grid(row=4, column=1, pady=2)

    # Actions
    def on_create():
        name = entry_name.get().strip()
        description = text_desc.get("1.0", tk.END).strip()
        license_name = entry_license.get().strip()
        keywords = [kw.strip() for kw in entry_keywords.get().split(",") if kw.strip()]

        if not name:
            messagebox.showerror("Error", "Plugin name is required.")
            return

        create_plugin_skeleton(name, description, license_name, keywords)
        messagebox.showinfo("Success", f"Plugin '{name}' created successfully!")

    tk.Button(root, text="Create Plugin", command=on_create).grid(row=5, column=0, pady=10)
    tk.Button(root, text="Exit", command=root.destroy).grid(row=5, column=1, pady=10)

    root.mainloop()
