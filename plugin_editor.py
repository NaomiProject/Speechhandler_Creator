# plugin_editor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import re
from plugin_generator import create_plugin_skeleton


PLACEHOLDER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")


class CustomAskString(simpledialog.Dialog):
    def __init__(self, parent, title, prompt, default=""):
        self.prompt = prompt
        self.default = default
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(pady=5)
        self.entry = tk.Entry(master, bg="white")
        self.entry.pack(pady=5)
        return self.entry  # Set initial focus

    def apply(self):
        """Process the data when OK is clicked."""
        self.result = self.entry.get()


class LocaleEditor(tk.Toplevel):
    """Edit one locale: keywords (dict[str, list[str]]) and templates (list[str])."""
    def __init__(self, master, initial=None, locale_code="en-US"):
        super().__init__(master)
        self.title(f"Locale: {locale_code}")
        self.resizable(False, False)
        self.result = None
        self.locale_code = locale_code
        self.keywords = dict((initial or {}).get("keywords", {}))
        self.templates = list((initial or {}).get("templates", []))

        # Keywords section
        row = 0
        ttk.Label(self, text="Keyword Categories").grid(row=row, column=0, padx=8, pady=6, sticky="w")
        kw_frame = ttk.Frame(self); kw_frame.grid(row=row, column=1, padx=8, pady=6, sticky="nsew")
        self.kw_list = tk.Listbox(kw_frame, width=45, height=8); self.kw_list.pack(side="left", fill="both", expand=True)
        kw_btns = ttk.Frame(kw_frame); kw_btns.pack(side="right", fill="y")
        ttk.Button(kw_btns, text="Add", width=10, command=self.add_kw).pack(pady=2)
        ttk.Button(kw_btns, text="Edit", width=10, command=self.edit_kw).pack(pady=2)
        ttk.Button(kw_btns, text="Delete", width=10, command=self.del_kw).pack(pady=2)

        # Templates
        row += 1
        ttk.Label(self, text="Templates (use {CategoryName})").grid(row=row, column=0, padx=8, pady=6, sticky="w")
        tm_frame = ttk.Frame(self); tm_frame.grid(row=row, column=1, padx=8, pady=6, sticky="nsew")
        self.tm_list = tk.Listbox(tm_frame, width=45, height=8); self.tm_list.pack(side="left", fill="both", expand=True)
        tm_btns = ttk.Frame(tm_frame); tm_btns.pack(side="right", fill="y")
        ttk.Button(tm_btns, text="Add", width=10, command=self.add_tm).pack(pady=2)
        ttk.Button(tm_btns, text="Edit", width=10, command=self.edit_tm).pack(pady=2)
        ttk.Button(tm_btns, text="Delete", width=10, command=self.del_tm).pack(pady=2)

        # Save/Cancel
        row += 1
        btns = ttk.Frame(self); btns.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Save", width=12, command=self.on_save).pack(side="left", padx=8)
        ttk.Button(btns, text="Cancel", width=12, command=self.destroy).pack(side="left", padx=8)

        self.refresh()

        self.grab_set()
        self.transient(master)

    def refresh(self):
        self.kw_list.delete(0, tk.END)
        for k in sorted(self.keywords.keys()):
            self.kw_list.insert(tk.END, f"{k}: {', '.join(self.keywords[k])}")
        self.tm_list.delete(0, tk.END)
        for t in self.templates:
            self.tm_list.insert(tk.END, t)

    def add_kw(self):
        dialog = CustomAskString(self, "Keyword Category", "Category name, e.g. DayKeyword:")
        name = dialog.result
        if not name:
            return
        if name in self.keywords:
            from tkinter import messagebox
            messagebox.showerror("Exists", "That category already exists.", parent=self)
            return
        dialog = CustomAskString(self, "Phrases", "Comma-separated phrases:")
        phrases = dialog.result
        vals = [p.strip() for p in phrases.split(",") if p.strip()]
        self.keywords[name] = vals
        self.refresh()

    def edit_kw(self):
        sel = self.kw_list.curselection()
        if not sel: return
        key = sorted(self.keywords.keys())[sel[0]]
        dialog = CustomAskString(self, "Rename", "New category name:", default=key)
        new_name = dialog.result
        if not new_name:
            return
        dialog = CustomAskString(self, "Phrases", "Edit comma-separated phrases:", default=", ".join(self.keywords[key]))
        phrases = dialog.result
        vals = [p.strip() for p in phrases.split(",") if p.strip()]
        if new_name != key and new_name in self.keywords:
            from tkinter import messagebox
            messagebox.showerror("Exists", "Category already exists.", parent=self)
            return
        if new_name != key:
            self.keywords[new_name] = vals
            del self.keywords[key]
        else:
            self.keywords[key] = vals
        self.refresh()

    def del_kw(self):
        sel = self.kw_list.curselection()
        if not sel:
            return
        key = sorted(self.keywords.keys())[sel[0]]
        # warn if templates reference {key}
        used = [t for t in self.templates if f"{{{key}}}" in t]
        if used:
            from tkinter import messagebox
            if not messagebox.askyesno("Referenced", f"Templates reference {{{key}}}. Delete anyway?", parent=self):
                return
        del self.keywords[key]
        self.refresh()

    def add_tm(self):
        dialog = CustomAskString(self, "Template", "Template text:")
        t = dialog.result
        if not t:
            return
        self.templates.append(t.strip()); self.refresh()

    def edit_tm(self):
        sel = self.tm_list.curselection()
        if not sel: return
        idx = sel[0]; t = self.templates[idx]
        dialog = CustomAskString(self, "Template", "Edit template:", initialvalue=t)
        nt = dialog.result
        if not nt:
            return
        self.templates[idx] = nt.strip()
        self.refresh()

    def del_tm(self):
        sel = self.tm_list.curselection()
        if not sel:
            return
        del self.templates[sel[0]]
        self.refresh()

    def on_save(self):
        # Validate placeholders exist as keyword categories
        cats = set(self.keywords.keys())
        missing = set()
        for t in self.templates:
            for ph in PLACEHOLDER_RE.findall(t):
                if ph not in cats:
                    missing.add(ph)
        if missing:
            from tkinter import messagebox
            messagebox.showerror(
                "Missing categories",
                "Placeholders missing keyword categories:\n" + ", ".join(sorted(missing)),
                parent=self
            )
            return
        self.result = {"keywords": self.keywords, "templates": self.templates}
        self.destroy()


class IntentEditor(tk.Toplevel):
    """Edit a full intent with multiple locales."""
    def __init__(self, master, initial=None):
        super().__init__(master)
        self.title("Intent Editor")
        self.resizable(False, False)
        self.result = None
        initial = initial or {"intent_name": "", "locales": {}}  # locales: { 'en-US': {keywords,templates}, ... }
        self.intent_name = tk.StringVar(value=initial.get("intent_name", ""))
        self.locales = dict(initial.get("locales", {}))

        row = 0
        ttk.Label(self, text="Intent Name").grid(row=row, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(self, width=32, textvariable=self.intent_name).grid(row=row, column=1, padx=8, pady=8, sticky="w")

        row += 1
        ttk.Label(self, text="Locales").grid(row=row, column=0, padx=8, sticky="nw")
        lf = ttk.Frame(self); lf.grid(row=row, column=1, padx=8, pady=8, sticky="nsew")
        self.loc_list = tk.Listbox(lf, width=40, height=10); self.loc_list.pack(side="left", fill="both", expand=True)
        btns = ttk.Frame(lf); btns.pack(side="right", fill="y")
        ttk.Button(btns, text="Add", width=10, command=self.add_locale).pack(pady=2)
        ttk.Button(btns, text="Edit", width=10, command=self.edit_locale).pack(pady=2)
        ttk.Button(btns, text="Delete", width=10, command=self.del_locale).pack(pady=2)

        row += 1
        pane = ttk.Frame(self); pane.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(pane, text="Save", command=self.on_save, width=12).pack(side="left", padx=6)
        ttk.Button(pane, text="Cancel", command=self.destroy, width=12).pack(side="left", padx=6)

        self.refresh_locales()
        self.grab_set()
        self.transient(master)

    def refresh_locales(self):
        self.loc_list.delete(0, tk.END)
        for code in sorted(self.locales.keys()):
            cats = ", ".join(sorted(self.locales[code].get("keywords", {}).keys()))
            tcount = len(self.locales[code].get("templates", []))
            self.loc_list.insert(tk.END, f"{code}    cats: [{cats}]    templates: {tcount}")

    def add_locale(self):
        dialog = CustomAskString(self, "Locale Code", "e.g., en-US, fr-FR:")
        code = dialog.result
        if not code:
            return
        if code in self.locales:
            messagebox.showerror("Exists", "Locale already exists.", parent=self); return
        dlg = LocaleEditor(self, initial={"keywords": {}, "templates": []}, locale_code=code)
        self.wait_window(dlg)
        if dlg.result:
            self.locales[code] = dlg.result
            self.refresh_locales()

    def edit_locale(self):
        sel = self.loc_list.curselection()
        if not sel: return
        code = sorted(self.locales.keys())[sel[0]]
        dlg = LocaleEditor(self, initial=self.locales[code], locale_code=code)
        self.wait_window(dlg)
        if dlg.result:
            self.locales[code] = dlg.result
            self.refresh_locales()

    def del_locale(self):
        sel = self.loc_list.curselection()
        if not sel: return
        code = sorted(self.locales.keys())[sel[0]]
        del self.locales[code]
        self.refresh_locales()

    def on_save(self):
        name = self.intent_name.get().strip()
        if not name:
            messagebox.showerror("Missing", "Intent name is required.", parent=self); return
        if not self.locales:
            messagebox.showerror("Missing", "Add at least one locale.", parent=self); return
        self.result = {"intent_name": name, "locales": self.locales}
        self.destroy()


class PluginEditor(ttk.Frame):
    """Main editor tab for plugin metadata and intents."""
    def __init__(self, parent):
        super().__init__(parent)
        self.plugin = {
            "name": "",
            "description": "",
            "license": "MIT",
            "intents": []  # list of {intent_name, locales:{code:{keywords,templates}}}
        }

        row = 0
        ttk.Label(self, text="Plugin Name").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.ent_name = ttk.Entry(self, width=40); self.ent_name.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        row += 1
        ttk.Label(self, text="Description").grid(row=row, column=0, padx=10, pady=2, sticky="nw")
        self.txt_desc = scrolledtext.ScrolledText(self, bg="white", width=56, height=6)
        self.txt_desc.grid(row=row, column=1, padx=10, pady=2, sticky="w")

        row += 1
        ttk.Label(self, text="License").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.ent_license = ttk.Entry(self, width=20)
        self.ent_license.insert(0, "MIT")
        self.ent_license.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        row += 1
        ttk.Label(self, text="Intents").grid(row=row, column=0, padx=10, pady=8, sticky="nw")
        it_frame = ttk.Frame(self); it_frame.grid(row=row, column=1, padx=10, pady=8, sticky="nsew")
        self.lb_intents = tk.Listbox(it_frame, width=60, height=10)
        self.lb_intents.pack(side="left", fill="both", expand=True)
        btns = ttk.Frame(it_frame); btns.pack(side="right", fill="y")
        ttk.Button(btns, text="Add", width=12, command=self.add_intent).pack(pady=2)
        ttk.Button(btns, text="Edit", width=12, command=self.edit_intent).pack(pady=2)
        ttk.Button(btns, text="Delete", width=12, command=self.del_intent).pack(pady=2)

        row += 1
        ttk.Button(self, text="Generate Plugin", command=self.generate).grid(row=row, column=0, columnspan=2, pady=14)

        # stretch
        self.grid_columnconfigure(1, weight=1)

    def refresh_intents(self):
        self.lb_intents.delete(0, tk.END)
        for it in self.plugin["intents"]:
            self.lb_intents.insert(tk.END, f"{it['intent_name']}  ({len(it['locales'])} locales)")

    def add_intent(self):
        dlg = IntentEditor(self)
        self.wait_window(dlg)
        if dlg.result:
            self.plugin["intents"].append(dlg.result)
            self.refresh_intents()

    def edit_intent(self):
        sel = self.lb_intents.curselection()
        if not sel: return
        obj = self.plugin["intents"][sel[0]]
        dlg = IntentEditor(self, initial=obj)
        self.wait_window(dlg)
        if dlg.result:
            self.plugin["intents"][sel[0]] = dlg.result
            self.refresh_intents()

    def del_intent(self):
        sel = self.lb_intents.curselection()
        if not sel: return
        del self.plugin["intents"][sel[0]]
        self.refresh_intents()

    def generate(self):
        name = self.ent_name.get().strip()
        desc = self.txt_desc.get("1.0", tk.END).strip()
        lic = self.ent_license.get().strip() or "MIT"
        if not name:
            messagebox.showerror("Missing", "Plugin name is required."); return
        if not self.plugin["intents"]:
            messagebox.showerror("Missing", "Add at least one intent."); return

        outdir = create_plugin_skeleton(
            name=name,
            description=desc,
            license_name=lic,
            intents=self.plugin["intents"]
        )
        messagebox.showinfo("Success", f"Created: {outdir}")
