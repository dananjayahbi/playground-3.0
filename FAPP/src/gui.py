import tkinter as tk
import sys
import ttkbootstrap as tkbs
from ttkbootstrap import ttk
from preview import PreviewFrame
from settings import (
    # TTK & window
    APP_BG_COLOR,
    RIGHT_PANEL_BG,
    TEXT_WIDGET_BG,
    TEXT_WIDGET_FG,
    TEXT_WIDGET_FONT,
    TTK_THEME,
)

class App(tkbs.Window):
    def __init__(self):
        # Pass the desired theme name to the tkbs.Window constructor
        super().__init__(themename=TTK_THEME)
        self.title("Motivational Quote Post Creator")
        self.geometry("1110x520")
        self.config(bg=APP_BG_COLOR)  # Dark theme background

        # Make sure the app closes fully when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure a 3-column grid:
        #   Column 0: Preview
        #   Column 1: Input area
        #   Column 2: Filler/Spacer
        self.columnconfigure(0, minsize=500)
        self.columnconfigure(1, minsize=500)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Preview Panel (Column 0) ---
        self.preview_frame = PreviewFrame(self)
        self.preview_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # --- Input Panel (Column 1) ---
        self.input_frame = tk.Frame(self, bg=RIGHT_PANEL_BG)
        self.input_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure the input_frame to have two rows:
        #   row 0 for the text box
        #   row 1 for the buttons
        self.input_frame.rowconfigure(0, weight=0)
        self.input_frame.rowconfigure(1, weight=0)
        self.input_frame.columnconfigure(0, weight=1)

        # --- Text Box (Row 0) ---
        self.text_input = tk.Text(
            self.input_frame,
            wrap="word",
            font=TEXT_WIDGET_FONT,
            bg=TEXT_WIDGET_BG,
            fg=TEXT_WIDGET_FG,
            width=50,
            height=4
        )
        self.text_input.grid(row=0, column=0, sticky="nsew", pady=10)

        # --- Buttons (Row 1) ---
        self.buttons_frame = tk.Frame(self.input_frame, bg=RIGHT_PANEL_BG)
        self.buttons_frame.grid(row=1, column=0, pady=10, sticky="n")

        self.update_button = ttk.Button(self.buttons_frame, text="Update Preview", command=self.update_preview)
        self.update_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(self.buttons_frame, text="Save Post", command=self.save_post)
        self.save_button.grid(row=0, column=1, padx=5)

        self.clear_button = ttk.Button(self.buttons_frame, text="Clear", command=self.clear_all)
        self.clear_button.grid(row=0, column=2, padx=5)

    def update_preview(self):
        quote = self.text_input.get("1.0", "end").strip()
        self.preview_frame.update_quote(quote)

    def save_post(self):
        # Just save the post, no pop-up message
        self.preview_frame.save_post()

    def clear_all(self):
        self.text_input.delete("1.0", "end")
        self.preview_frame.clear()

    def on_closing(self):
        """Cleanly close the app and terminate the Python process."""
        self.destroy()
        sys.exit(0)
