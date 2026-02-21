import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import json

import matplotlib
matplotlib.use("Agg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from ai_core import graph, data_description, llm, get_llm

BG_MAIN = "#1e1e1e"
BG_PANEL = "#252526"
BG_INPUT = "#2d2d2d"
FG_TEXT = "#d4d4d4"
ACCENT = "#0e639c"

FONT_UI = ("Segoe UI", 10)
FONT_CODE = ("Consolas", 10)

# Theme definitions
THEMES = {
    "dark": {
        "BG_MAIN": "#1e1e1e",
        "BG_PANEL": "#252526",
        "BG_INPUT": "#2d2d2d",
        "FG_TEXT": "#d4d4d4",
        "ACCENT": "#0e639c",
    },
    "light": {
        "BG_MAIN": "#ffffff",
        "BG_PANEL": "#f3f3f3",
        "BG_INPUT": "#eeeeee",
        "FG_TEXT": "#333333",
        "ACCENT": "#0078d4",
    }
}

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return get_default_config()
    return get_default_config()

def get_default_config():
    """Return default configuration"""
    return {
        "theme": "",
        "llm_backend": "",
        "groq_api_key": "",
        "openai_api_key": "",
        "ollama_model": ""
    }

def save_config(config):
    """Save configuration to config.json"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


class SettingsDialog:
    """Settings dialog for configuring Theme and LLM"""

    def __init__(self, parent, config, on_settings_change):
        self.config = config
        self.on_settings_change = on_settings_change
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("450x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.build_dialog()

        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def build_dialog(self):
        """Build the settings dialog UI"""
        main_frame = tk.Frame(self.dialog, bg=BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Theme Section
        tk.Label(main_frame, text="Theme", bg=BG_MAIN, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        theme_frame = tk.Frame(main_frame, bg=BG_INPUT, relief="flat")
        theme_frame.pack(fill="x", pady=(0, 15))

        self.theme_var = tk.StringVar(value=self.config.get("theme", "dark"))

        for theme in ["Dark", "Light"]:
            tk.Radiobutton(theme_frame, text=theme, variable=self.theme_var,
                          value=theme.lower(), bg=BG_INPUT, fg=FG_TEXT,
                          selectcolor=BG_INPUT).pack(side="left", padx=10, pady=8)

        # LLM Backend Section
        tk.Label(main_frame, text="LLM Backend", bg=BG_MAIN, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        llm_frame = tk.Frame(main_frame, bg=BG_INPUT, relief="flat")
        llm_frame.pack(fill="x", pady=(0, 15))

        self.llm_var = tk.StringVar(value=self.config.get("llm_backend", "groq"))

        for llm in ["Groq", "Ollama", "OpenAI"]:
            tk.Radiobutton(llm_frame, text=llm, variable=self.llm_var,
                          value=llm.lower(), bg=BG_INPUT, fg=FG_TEXT,
                          selectcolor=BG_INPUT).pack(side="left", padx=10, pady=8)

        # API Key Section
        tk.Label(main_frame, text="API Configuration", bg=BG_MAIN, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 8))

        api_frame = tk.Frame(main_frame, bg=BG_MAIN)
        api_frame.pack(fill="x", pady=(0, 15))

        tk.Label(api_frame, text="Groq API Key:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", pady=(0, 4))
        self.groq_entry = tk.Entry(api_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground="white")
        self.groq_entry.pack(fill="x", pady=(0, 10))
        self.groq_entry.insert(0, self.config.get("groq_api_key", ""))

        tk.Label(api_frame, text="OpenAI API Key:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", pady=(0, 4))
        self.openai_entry = tk.Entry(api_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground="white")
        self.openai_entry.pack(fill="x", pady=(0, 10))
        self.openai_entry.insert(0, self.config.get("openai_api_key", ""))

        tk.Label(api_frame, text="Ollama Model:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", pady=(0, 4))
        self.ollama_entry = tk.Entry(api_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground="white")
        self.ollama_entry.pack(fill="x")
        self.ollama_entry.insert(0, self.config.get("ollama_model", "llama3.1:8b"))

        # Buttons
        button_frame = tk.Frame(main_frame, bg=BG_MAIN)
        button_frame.pack(fill="x", pady=(10, 0))

        tk.Button(button_frame, text="Save", bg=ACCENT, fg="white", relief="flat",
                 command=self.save_settings).pack(side="right", padx=(5, 0))
        tk.Button(button_frame, text="Cancel", bg="#555555", fg="white", relief="flat",
                 command=self.dialog.destroy).pack(side="right", padx=5)

    def save_settings(self):
        """Save the settings and call the callback"""
        new_config = {
            "theme": self.theme_var.get(),
            "llm_backend": self.llm_var.get(),
            "groq_api_key": self.groq_entry.get().strip(),
            "openai_api_key": self.openai_entry.get().strip(),
            "ollama_model": self.ollama_entry.get().strip()
        }

        try:
            save_config(new_config)
            self.on_settings_change(new_config)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}\n\nMake sure you have the required package installed for the selected LLM backend.")


class DataAnalystApp:

    def __init__(self, root):
        self.root = root
        self.root.title("AI Data Analyst")
        self.root.geometry("1400x850")

        # Load configuration from config.json
        self.config = load_config()
        self.apply_theme(self.config.get("theme", "dark"))
        self.root.configure(bg=self.bg_main)

        # Note: ai_core.py initializes LLM from config.json automatically

        self.dfs = []
        self.state = None

        self.mode = tk.StringVar(value="chat")
        self.bottom_tab = tk.StringVar(value="summary")
        self.transform_mode = tk.StringVar(value="Python Mode")

        self.build_layout()

        self.root.bind_all("<MouseWheel>", self._global_mousewheel, add=True)
        self.root.bind_all("<Button-4>", self._global_mousewheel, add=True)
        self.root.bind_all("<Button-5>", self._global_mousewheel, add=True)

    def apply_theme(self, theme_name):
        """Apply theme colors to the app"""
        theme = THEMES.get(theme_name, THEMES["dark"])
        self.bg_main = theme["BG_MAIN"]
        self.bg_panel = theme["BG_PANEL"]
        self.bg_input = theme["BG_INPUT"]
        self.fg_text = theme["FG_TEXT"]
        self.accent = theme["ACCENT"]

    def on_settings_changed(self, new_config):
        """Handle settings change"""
        self.config = new_config
        theme_changed = self.config.get("theme", "dark")

        # Apply theme
        self.apply_theme(theme_changed)

        # Update LLM if backend changed
        llm_backend = self.config.get("llm_backend", "groq")
        groq_key = self.config.get("groq_api_key", "")
        openai_key = self.config.get("openai_api_key", "")
        ollama_model = self.config.get("ollama_model", "llama3.1:8b")

        # Update the global llm object in ai_core module
        import ai_core
        ai_core.llm = get_llm(llm_backend, groq_key, openai_key, ollama_model)

        messagebox.showinfo("Settings", "Settings updated successfully!\nPlease restart the app for full theme changes to apply.")

    def open_settings(self):
        """Open the settings dialog"""
        SettingsDialog(self.root, self.config, self.on_settings_changed)

    # ---------------- LAYOUT ----------------

    def build_layout(self):

        top_bar = tk.Frame(self.root, bg=BG_PANEL, height=35)
        top_bar.pack(fill="x")

        self._mode_button(top_bar, "Chat Mode", "chat")
        self._mode_button(top_bar, "Data & Transformations", "data")

        self.main_vertical = tk.PanedWindow(self.root, orient="vertical", sashwidth=6)
        self.main_vertical.pack(fill="both", expand=True)

        self.main_horizontal = tk.PanedWindow(self.main_vertical, orient="horizontal", sashwidth=6)
        self.main_vertical.add(self.main_horizontal)

        self.sidebar = tk.Frame(self.main_horizontal, bg=BG_PANEL)
        self.main_horizontal.add(self.sidebar)

        tk.Label(self.sidebar, text="📦 IN CONTEXT", bg=BG_PANEL,
                 fg=FG_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=8)

        self.ledger_list = tk.Listbox(
            self.sidebar,
            bg=BG_PANEL,
            fg=FG_TEXT,
            selectbackground=ACCENT,
            relief="flat",
            font=FONT_UI,
            height=12
        )
        self.ledger_list.pack(fill="both", expand=True, padx=8)

        ttk.Button(self.sidebar, text="Upload Files", command=self.upload_files)\
            .pack(fill="x", padx=8, pady=6)

        ttk.Button(self.sidebar, text="Remove Selected", command=self.remove_selected_df)\
            .pack(fill="x", padx=8, pady=4)

        self.canvas_container = tk.Frame(self.main_horizontal, bg=BG_MAIN)
        self.main_horizontal.add(self.canvas_container)

        self.build_chat_view()
        self.build_data_view()

        self.bottom_panel = tk.Frame(self.main_vertical, bg=BG_PANEL, height=220)
        self.main_vertical.add(self.bottom_panel)

        tab_bar = tk.Frame(self.bottom_panel, bg=BG_PANEL)
        tab_bar.pack(fill="x")

        # Left side tabs
        left_tabs = tk.Frame(tab_bar, bg=BG_PANEL)
        left_tabs.pack(side="left")

        self._bottom_tab(left_tabs, "Summary", "summary")
        self._bottom_tab(left_tabs, "Generated Code", "code")

        # Right side - Settings button
        right_buttons = tk.Frame(tab_bar, bg=BG_PANEL)
        right_buttons.pack(side="right", padx=8)

        tk.Button(right_buttons, text="⚙ Settings", bg=ACCENT, fg="white", relief="flat",
                 command=self.open_settings).pack(side="right")

        self.bottom_text = tk.Text(self.bottom_panel, bg="#1b1b1b",
                                   fg=FG_TEXT, relief="flat", font=FONT_CODE)
        self.bottom_text.pack(fill="both", expand=True)

        self.root.update_idletasks()
        self.main_horizontal.sash_place(0, 220, 0)
        self.main_vertical.sash_place(0, 0, 450)

        self.switch_mode()

    # ---------------- CHAT VIEW ----------------

    def build_chat_view(self):

        self.chat_frame = tk.Frame(self.canvas_container, bg=BG_MAIN)

        query_bar = tk.Frame(self.chat_frame, bg=BG_MAIN)
        query_bar.pack(fill="x", padx=10, pady=10)

        self.query_entry = tk.Entry(query_bar, bg=BG_INPUT, fg=FG_TEXT,
                                    insertbackground="white")
        self.query_entry.pack(side="left", fill="x", expand=True, ipady=6)

        tk.Button(query_bar, text="Run", bg=ACCENT, fg="white",
                  relief="flat", command=self.run_analysis).pack(side="left", padx=6)

        container = tk.Frame(self.chat_frame, bg=BG_MAIN)
        container.pack(fill="both", expand=True)

        self.chat_canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.chat_canvas.yview)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        self.chat_inner = tk.Frame(self.chat_canvas, bg=BG_MAIN)
        self.chat_canvas.create_window((0, 0), window=self.chat_inner, anchor="nw")

        self.chat_inner.bind("<Configure>", lambda e:
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

    # ---------------- DATA VIEW ----------------

    def build_data_view(self):

        self.data_frame = tk.Frame(self.canvas_container, bg=BG_MAIN)

        top = tk.Frame(self.data_frame, bg=BG_MAIN)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="DataFrame:", bg=BG_MAIN, fg=FG_TEXT).pack(side="left")

        self.df_selector = ttk.Combobox(top, state="readonly", width=30)
        self.df_selector.pack(side="left", padx=5)

        ttk.Button(top, text="Preview", command=self.preview_df).pack(side="left")

        self.preview_box = tk.Text(self.data_frame, bg="#1b1b1b",
                                   fg=FG_TEXT, font=FONT_CODE, height=14)
        self.preview_box.pack(fill="both", expand=True, padx=10)

        mode_bar = tk.Frame(self.data_frame, bg=BG_MAIN)
        mode_bar.pack(fill="x", padx=10)

        ttk.Radiobutton(mode_bar, text="Python Mode",
                        variable=self.transform_mode, value="Python Mode").pack(side="left")

        ttk.Radiobutton(mode_bar, text="LLM Mode",
                        variable=self.transform_mode, value="LLM Mode").pack(side="left", padx=10)

        self.transform_box = tk.Text(self.data_frame, bg=BG_INPUT,
                                     fg=FG_TEXT, font=FONT_CODE, height=6)
        self.transform_box.pack(fill="x", padx=10, pady=5)

        tk.Button(self.data_frame, text="Apply Data Transformation",
                  bg=ACCENT, fg="white", relief="flat",
                  command=self.apply_transformation)\
            .pack(anchor="e", padx=10, pady=5)

    # ---------------- ANALYSIS ----------------

    def run_analysis(self):

        query = self.query_entry.get().strip()
        if not query or not self.dfs:
            messagebox.showwarning("Missing Input", "Upload data & enter query")
            return

        self._chat("USER", query)

        state = {"dfs": self.dfs, "user_query": query}
        self.state = graph.invoke(state)

        self._chat("AI", self.state.get("execution_output", ""))
        self.update_bottom_panel()
        self.update_ledger()
        self.render_figures_inline()

    # ---------------- REMOVE DF ----------------

    def remove_selected_df(self):

        selection = self.ledger_list.curselection()

        if not selection:
            messagebox.showwarning("No Selection", "Select a DataFrame to remove")
            return

        df_name = self.ledger_list.get(selection[0])

        self.dfs = [d for d in self.dfs if d["name"] != df_name]

        if self.state and "context_ledger" in self.state:
            self.state["context_ledger"].pop(df_name, None)

        self.update_ledger()
        self.preview_box.delete("1.0", "end")

        messagebox.showinfo("Removed", f"{df_name} removed from context")

    # ---------------- TRANSFORM ----------------

    def apply_transformation(self):

        name = self.df_selector.get()
        instruction = self.transform_box.get("1.0", "end").strip()

        if not name or not instruction:
            messagebox.showwarning("Missing Input", "Select DF & enter transformation")
            return

        target = next((d for d in self.dfs if d["name"] == name), None)

        try:
            if self.transform_mode.get() == "LLM Mode":

                prompt = f"""
Return ONLY valid Python code.

Modify pandas DataFrame '{name}' according to:

{instruction}

Rules:
- No explanations
- No markdown
- Only Python code
"""

                code = llm.invoke(prompt).strip()
                if "```" in code:
                    code = code.replace("```python", "").replace("```", "").strip()

            else:
                code = instruction

            local_vars = {name: target["data"]}
            exec(code, {}, local_vars)

            target["data"] = local_vars[name]

            self.preview_df()

            messagebox.showinfo("Success", f"{name} updated")

        except Exception as e:
            messagebox.showerror("Transformation Error", str(e))

    # ---------------- UI HELPERS ----------------

    def _chat(self, sender, text):
        block = tk.Frame(self.chat_inner, bg=BG_MAIN)
        block.pack(fill="x", padx=8, pady=4)

        tk.Label(block, text=sender, fg=ACCENT if sender == "AI" else FG_TEXT,
                 bg=BG_MAIN).pack(anchor="w")

        tk.Label(block, text=text, fg=FG_TEXT,
                 bg=BG_MAIN, wraplength=900, justify="left").pack(anchor="w")

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def render_figures_inline(self):
        if not self.state:
            return
        for path in self.state.get("figure_paths", []):
            if os.path.exists(path):
                fig = plt.figure()
                img = plt.imread(path)
                plt.imshow(img)
                plt.axis("off")
                canvas = FigureCanvasTkAgg(fig, master=self.chat_inner)
                canvas.draw()
                canvas.get_tk_widget().pack(anchor="w")

    def update_ledger(self):
        self.ledger_list.delete(0, "end")
        if not self.state:
            return
        for k in self.state.get("context_ledger", {}):
            self.ledger_list.insert("end", k)
        self.df_selector["values"] = [d["name"] for d in self.dfs]

    def preview_df(self):
        name = self.df_selector.get()
        df = next((d["data"] for d in self.dfs if d["name"] == name), None)
        if df is not None:
            self.preview_box.delete("1.0", "end")
            self.preview_box.insert("end", df.head(25).to_string())

    def upload_files(self):
        for path in filedialog.askopenfilenames(filetypes=[("Data Files", "*.csv *.xlsx *.xls")]):
            df = pd.read_csv(path) if path.endswith(".csv") else pd.read_excel(path)
            self.dfs.append({"name": os.path.splitext(os.path.basename(path))[0],
                             "data": df,
                             "description": path})
        self.df_selector["values"] = [d["name"] for d in self.dfs]

    def update_bottom_panel(self):
        self.bottom_text.delete("1.0", "end")
        if not self.state:
            return
        key = "analysis" if self.bottom_tab.get() == "summary" else "generated_code"
        self.bottom_text.insert("end", self.state.get(key, ""))

    def _bottom_tab(self, parent, label, value):
        tk.Radiobutton(parent, text=label, variable=self.bottom_tab, value=value,
                       indicatoron=0, bg=BG_PANEL, fg=FG_TEXT,
                       selectcolor="#333333", relief="flat",
                       command=self.update_bottom_panel).pack(side="left")

    def _mode_button(self, parent, label, value):
        tk.Radiobutton(parent, text=label, variable=self.mode, value=value,
                       indicatoron=0, bg=BG_PANEL, fg=FG_TEXT,
                       selectcolor="#333333", relief="flat",
                       command=self.switch_mode).pack(side="left")

    def switch_mode(self):
        for w in (self.chat_frame, self.data_frame):
            w.pack_forget()
        (self.chat_frame if self.mode.get() == "chat" else self.data_frame)\
            .pack(fill="both", expand=True)

    def _global_mousewheel(self, event):
        widget = event.widget
        while widget:
            if widget == self.chat_canvas:
                self.chat_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
                return
            widget = widget.master


if __name__ == "__main__":
    root = tk.Tk()
    DataAnalystApp(root)
    root.mainloop()