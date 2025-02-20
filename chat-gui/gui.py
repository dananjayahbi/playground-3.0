import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import google.generativeai as genai
import os
import threading
from PIL import Image, ImageTk

# Additional imports for Markdown parsing
import markdown
from tkhtmlview import HTMLLabel

# Configure Gemini API (replace with your API key)
GOOGLE_API_KEY = "AIzaSyCse9GTefXoELj33YCbmkRinG2JQc7AHQo"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class ChatbotApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        
        self.title("Gemini Chat 🤖")
        self.geometry("1920x1080")
        self.state("zoomed")

        # Chat width 1024px, centered
        self.min_chat_width = 1024

        # Load icons
        icon_size = (30, 30)
        if os.path.exists("user_icon.png"):
            user_img = Image.open("user_icon.png").resize(icon_size, Image.LANCZOS)
            self.user_icon = ImageTk.PhotoImage(user_img)
        else:
            self.user_icon = None
        
        if os.path.exists("robot_icon.png"):
            ai_img = Image.open("robot_icon.png").resize(icon_size, Image.LANCZOS)
            self.ai_icon = ImageTk.PhotoImage(ai_img)
        else:
            self.ai_icon = None

        self.message_count = 0  # Track number of messages

        self.create_widgets()
        self.setup_chat()

    def create_widgets(self):
        """
        Layout:
        - chat_container: Holds only messages and input area (1024px, centered)
        - Scrollbar is OUTSIDE chat_container, at far right of the window
        """
        # 1) Main container (fills entire window)
        main_frame = tk.Frame(self, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True)

        # 2) Scrollbar on the far right (outside chat_container)
        self.scrollbar = tb.Scrollbar(main_frame, orient='vertical')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 3) Centered Chat Container (1024px)
        self.chat_container = tk.Frame(main_frame, bg='#2d2d2d', width=self.min_chat_width)
        self.chat_container.place(relx=0.5, rely=0, anchor='n', relheight=1.0)
        self.chat_container.pack_propagate(False)

        # 4) Canvas inside chat_container
        self.chat_canvas = tk.Canvas(
            self.chat_container,
            bg='#2d2d2d',
            highlightthickness=0,
            bd=0,
            yscrollcommand=self.scrollbar.set
        )
        self.chat_canvas.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.chat_canvas.yview)

        # 5) Messages frame inside canvas (single column layout)
        self.messages_frame = tk.Frame(self.chat_canvas, bg='#2d2d2d')
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor='n')

        # 6) Force a single column of at least 1024px width
        self.messages_frame.grid_columnconfigure(0, minsize=self.min_chat_width)

        # --- ✅ Adjust Scroll Region Dynamically ---
        def update_scroll_region(event=None):
            """
            Updates the scroll region so the scrollbar behaves correctly.
            """
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

        # Bind updates
        self.messages_frame.bind("<Configure>", update_scroll_region)
        self.chat_canvas.bind("<Configure>", update_scroll_region)

        # Enable mouse wheel scrolling on Windows
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # 7) Input area (inside chat_container, centered)
        input_frame = tk.Frame(self.chat_container, bg='#2d2d2d')
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10), padx=10)

        self.user_input = tb.Entry(input_frame, font=('Arial', 12), bootstyle="light")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        send_btn = tb.Button(input_frame, text="Send", command=self.send_message, bootstyle="primary")
        send_btn.pack(side=tk.LEFT)

    def on_mousewheel(self, event):
        """Enable mouse wheel scrolling on Windows."""
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def setup_chat(self):
        # Start the chat and display the initial greeting message
        self.chat = model.start_chat(history=[])
        self.add_message("AI", "Hello! How can I help you today?")

    def add_message(self, sender, message):
        """
        Creates a chat bubble with Markdown rendering and inline styling.
        - AI messages are left-aligned with the AI icon.
        - User messages are right-aligned with the User icon.
        """

        # Convert Markdown to HTML
        html_content = markdown.markdown(message, extensions=["fenced_code", "tables"])

        # Apply inline styles directly
        styled_html = f"""
        <div style="color: #ffffff; font-family: Arial, sans-serif; font-size: 12px; border-radius: 20px; padding: 50px 0;">
            {html_content}
        </div>
        """

        container = tk.Frame(self.messages_frame, bg='#2d2d2d')

        if sender == "AI":
            container.grid(row=self.message_count, column=0, sticky='nw', padx=5, pady=5)
        else:
            container.grid(row=self.message_count, column=0, sticky='ne', padx=5, pady=5)

        msg_frame = tk.Frame(container, bg='#2d2d2d')

        if sender == "AI":
            # AI: icon on the left, bubble on the right
            msg_frame.pack(side='left', anchor='nw')

            if self.ai_icon:
                icon_label = tk.Label(msg_frame, image=self.ai_icon, bg='#2d2d2d')
                icon_label.pack(side='left', anchor='nw', padx=(0,5))

            # Bubble frame (consistent bg color)
            bubble_frame = tk.Frame(msg_frame, bg="#6c757d")
            bubble_frame.pack(side='left', anchor='nw')

            bubble_label = HTMLLabel(
                bubble_frame,
                html=styled_html,
                background="#6c757d",
                width=80
            )
            bubble_label.pack(side='left', anchor='nw', padx=10, pady=5)
            bubble_label.fit_height()

        else:
            # User: bubble on the right, icon after the bubble
            msg_frame.pack(side='right', anchor='ne')

            bubble_frame = tk.Frame(msg_frame, bg="#0d6efd")
            bubble_frame.pack(side='right', anchor='ne')

            bubble_label = HTMLLabel(
                bubble_frame,
                html=styled_html,
                background="#0d6efd",
                width=80
            )
            bubble_label.pack(side='right', anchor='ne', padx=10, pady=5)
            bubble_label.fit_height()

            if self.user_icon:
                icon_label = tk.Label(msg_frame, image=self.user_icon, bg='#2d2d2d')
                icon_label.pack(side='right', anchor='ne', padx=(5,0))

        self.message_count += 1

        # Auto-scroll to the bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def send_message(self):
        user_text = self.user_input.get()
        if not user_text.strip():
            return

        self.add_message("User", user_text)
        self.user_input.delete(0, tk.END)
        self.user_input.config(state=tk.DISABLED)

        # Get AI response in background
        threading.Thread(target=self.get_ai_response, args=(user_text,), daemon=True).start()

    def get_ai_response(self, user_text):
        try:
            response = self.chat.send_message(user_text)
            self.after(0, self.add_message, "AI", response.text)
        except Exception as e:
            self.after(0, self.show_error, str(e))
        finally:
            self.after(0, lambda: self.user_input.config(state=tk.NORMAL))

    def show_error(self, message):
        messagebox.showerror("Error", f"An error occurred:\n{message}")

if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
