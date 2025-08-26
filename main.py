#!/usr/bin/env python3
# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from plugin_editor import PluginEditor
from publisher import publish_plugin_folder, _read_plugin_info
import logging


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Naomi Plugin Tool")
        self.geometry("980x720")
        self._logger = logging.getLogger(__name__)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Editor tab
        self.editor = PluginEditor(nb)
        nb.add(self.editor, text="Plugin Editor")

        # Publish tab
        self.pub_tab = ttk.Frame(nb)
        nb.add(self.pub_tab, text="Publish")
        self._build_publish_tab()

    def _build_publish_tab(self):
        f = self.pub_tab

        row = 0
        ttk.Label(f, text="GitHub Username").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.gh_user = ttk.Entry(f, width=40)
        self.gh_user.grid(row=row, column=1, sticky="w", padx=10, pady=8)

        row += 1
        ttk.Label(f, text="GitHub Token (for PR & fork)").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.gh_token = ttk.Entry(f, width=60, show="*")
        self.gh_token.grid(row=row, column=1, sticky="w", padx=10, pady=8)

        row += 1
        ttk.Label(f, text="Plugin Folder").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        pf_row = ttk.Frame(f); pf_row.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.plugin_folder = ttk.Entry(pf_row, width=60)
        self.plugin_folder.pack(side="left")
        ttk.Button(pf_row, text="Browse", command=self._pick_folder).pack(side="left", padx=6)

        row += 1
        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        row += 1
        ttk.Label(f, text="Detected from plugin.info").grid(row=row, column=0, sticky="w", padx=10, pady=4)

        row += 1
        ttk.Label(f, text="Plugin Name").grid(row=row, column=0, sticky="w", padx=10, pady=4)
        self.name_val = ttk.Entry(f, width=50); self.name_val.grid(row=row, column=1, sticky="w", padx=10, pady=4)

        row += 1
        ttk.Label(f, text="Repo URL (SSH)").grid(row=row, column=0, sticky="w", padx=10, pady=4)
        self.repo_val = ttk.Entry(f, width=70); self.repo_val.grid(row=row, column=1, sticky="w", padx=10, pady=4)

        row += 1
        ttk.Label(f, text="License").grid(row=row, column=0, sticky="w", padx=10, pady=4)
        self.license_val = ttk.Entry(f, width=30); self.license_val.grid(row=row, column=1, sticky="w", padx=10, pady=4)

        row += 1
        ttk.Button(f, text="Publish (Push + PR)", command=self._do_publish).grid(row=row, column=0, columnspan=2, pady=18)

        # stretch cols
        f.grid_columnconfigure(1, weight=1)

    def _pick_folder(self):
        folder = filedialog.askdirectory(title="Select Plugin Folder")
        if not folder:
            return
        self.plugin_folder.delete(0, "end")
        self.plugin_folder.insert(0, folder)

        try:
            info = _read_plugin_info(folder)
            self.name_val.delete(0, "end"); self.name_val.insert(0, info.get("name", ""))
            self.repo_val.delete(0, "end"); self.repo_val.insert(0, info.get("repo_url", ""))
            self.license_val.delete(0, "end"); self.license_val.insert(0, info.get("license", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read plugin.info: {e}")
            self._logger.error(f"Failed to read plugin.info: {e}", exc_info=True)

    def _do_publish(self):
        folder = self.plugin_folder.get().strip()
        token = self.gh_token.get().strip()
        user = self.gh_user.get().strip()

        if not folder or not token or not user:
            messagebox.showerror("Missing info", "Please provide GitHub username, token, and plugin folder.")
            return

        try:
            pr_url = publish_plugin_folder(folder, token, user)
            messagebox.showinfo("Success", f"Pull Request created:\n{pr_url}")
        except Exception as e:
            messagebox.showerror("Publish failed", str(e))


if __name__ == "__main__":
    App().mainloop()
