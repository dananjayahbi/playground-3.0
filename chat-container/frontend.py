import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import requests
import os
import threading
from PIL import Image, ImageTk
import markdown
from tkhtmlview import HTMLLabel
import subprocess
import time
import torch
import whisper
import pyaudio
import wave
import json

# Backend API URL
API_URL = "http://127.0.0.1:8000/chat"

class ChatbotApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("TinyLlama Chat 🤖")
        self.geometry("1920x1080")
        self.state("zoomed")
        self.min_chat_width = 1024

        # Load icons
        icon_size = (30, 30)
        self.user_icon = ImageTk.PhotoImage(
            Image.open("assets/user_icon.png").resize(icon_size, Image.LANCZOS)
        ) if os.path.exists("assets/user_icon.png") else None
        self.ai_icon = ImageTk.PhotoImage(
            Image.open("assets/robot_icon.png").resize(icon_size, Image.LANCZOS)
        ) if os.path.exists("assets/robot_icon.png") else None

        self.message_count = 0

        # Conversation history (each entry is already formatted, e.g. "[USER]: Hi")
        self.conversation_history = []

        # Voice-based input using Whisper
        self.is_recording = False
        self.audio_file = "recorded_audio.wav"
        self.model = None  # To be loaded from models/base.pt

        self.create_widgets()
        self.add_message("AI", "Hello! How can I help you today?")  # Welcome message
        # Load the Whisper model asynchronously
        threading.Thread(target=self.load_model, daemon=True).start()

    def create_widgets(self):
        """Creates the chat UI."""
        main_frame = tk.Frame(self, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True)

        # Scrollbar
        self.scrollbar = tb.Scrollbar(main_frame, orient='vertical')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Chat Container
        self.chat_container = tk.Frame(main_frame, bg='#2d2d2d', width=self.min_chat_width)
        self.chat_container.place(relx=0.5, rely=0, anchor='n', relheight=1.0)
        self.chat_container.pack_propagate(False)

        # Canvas
        self.chat_canvas = tk.Canvas(
            self.chat_container,
            bg='#2d2d2d',
            highlightthickness=0,
            bd=0,
            yscrollcommand=self.scrollbar.set
        )
        self.chat_canvas.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.chat_canvas.yview)

        # Messages Frame
        self.messages_frame = tk.Frame(self.chat_canvas, bg='#2d2d2d')
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor='n')
        self.messages_frame.bind("<Configure>", lambda event: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.messages_frame.grid_columnconfigure(0, minsize=self.min_chat_width)

        def update_scroll_region(event=None):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.messages_frame.bind("<Configure>", update_scroll_region)
        self.chat_canvas.bind("<Configure>", update_scroll_region)
        self.bind_mouse_scroll()

        # Input area
        input_frame = tk.Frame(self.chat_container, bg='#2d2d2d')
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10), padx=10)

        self.user_input = tb.Entry(input_frame, font=('Arial', 12), bootstyle="light")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        # 🎤 Speak Button
        self.speak_btn = tb.Button(input_frame, text="🎤 Speak", command=self.recognize_speech, bootstyle="warning")
        self.speak_btn.pack(side=tk.RIGHT, padx=(5, 0))

        send_btn = tb.Button(input_frame, text="Send", command=self.send_message, bootstyle="primary")
        send_btn.pack(side=tk.RIGHT)

    def bind_mouse_scroll(self):
        """Ensures smooth scrolling across platforms."""
        self.chat_canvas.bind_all("<MouseWheel>", lambda e: self.chat_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.chat_canvas.bind_all("<Button-4>", lambda e: self.chat_canvas.yview_scroll(-1, "units"))
        self.chat_canvas.bind_all("<Button-5>", lambda e: self.chat_canvas.yview_scroll(1, "units"))

    def add_message(self, sender, message):
        """Creates a chat bubble with Markdown rendering and updates conversation history."""
        html_content = markdown.markdown(message, extensions=["fenced_code", "tables"])
        styled_html = f"""
        <div style="color: #ffffff; font-family: Arial, sans-serif; font-size: 14px; border-radius: 10px; padding: 10px;">
            {html_content}
        </div>
        """
        container = tk.Frame(self.messages_frame, bg='#2d2d2d')
        container.grid(row=self.message_count, column=0, sticky='ne' if sender == "User" else 'nw', padx=5, pady=5)
        msg_frame = tk.Frame(container, bg='#2d2d2d')
        msg_frame.pack(side='right' if sender == "User" else 'left', anchor='ne' if sender == "User" else 'nw')
        if sender == "User" and self.user_icon:
            tk.Label(msg_frame, image=self.user_icon, bg='#2d2d2d').pack(side='right', padx=(5, 0))
        bubble_frame = tk.Frame(msg_frame, bg="#0d6efd" if sender == "User" else "#6c757d")
        bubble_frame.pack(side='right' if sender == "User" else 'left')
        bubble_label = HTMLLabel(bubble_frame, html=styled_html, background="#0d6efd" if sender == "User" else "#6c757d", width=80)
        bubble_label.pack(side='right' if sender == "User" else 'left', padx=10, pady=5)
        bubble_label.fit_height()
        if sender == "AI" and self.ai_icon:
            tk.Label(msg_frame, image=self.ai_icon, bg='#2d2d2d').pack(side='left', padx=(0, 5))
        self.message_count += 1
        self.chat_canvas.yview_moveto(1.0)

    def load_model(self):
        """Loads the Whisper model from the local models/ folder asynchronously."""
        self.add_message("AI", "Loading Whisper model... Please wait.")
        try:
            model_path = os.path.join("models", "base.pt")  # Ensure this matches your file name
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if not os.path.exists(model_path):
                self.add_message("AI", "Error: Model file not found in models/ folder.")
                return
            self.model = whisper.load_model(model_path, device=device)
            self.add_message("AI", f"Whisper model loaded successfully from models/ on {device.upper()}!")
        except Exception as e:
            self.add_message("AI", f"Error loading model: {e}")

    def recognize_speech(self):
        """Toggles voice recording and transcribes speech using Whisper."""
        if not self.is_recording:
            self.add_message("AI", "Listening... Click again to stop.")
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.recording_thread.start()
            self.speak_btn.config(text="🛑 Stop")
        else:
            self.is_recording = False
            self.recording_thread.join()
            self.speak_btn.config(text="🎤 Speak")
            if os.path.exists(self.audio_file):
                text = self.transcribe_audio(self.audio_file)
                if text.strip():
                    self.add_message("User", text)
                    self.user_input.delete(0, tk.END)
                    self.user_input.insert(0, text)
                    self.send_message()  # Automatically send the transcribed text
                else:
                    self.add_message("AI", "I couldn't understand. Please try again.")
            else:
                self.add_message("AI", "Error: Audio file not saved properly.")

    def record_audio(self):
        """Records audio at 16kHz, 16-bit Mono and saves it as a WAV file."""
        RATE, CHUNK, FORMAT, CHANNELS = 16000, 4096, pyaudio.paInt16, 1
        mic = pyaudio.PyAudio()
        try:
            stream = mic.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            while self.is_recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            mic.terminate()
            with wave.open(self.audio_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(mic.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
        except Exception as e:
            self.add_message("AI", f"Recording error: {e}")

    def transcribe_audio(self, file_path):
        """Transcribes speech from an audio file using Whisper."""
        if self.model is None:
            return "Error: Whisper model not loaded."
        try:
            result = self.model.transcribe(file_path)
            return result["text"].strip()
        except Exception as e:
            return f"Transcription error: {e}"

    def send_message(self):
        """Sends user message along with conversation history to the backend and updates history."""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.add_message("User", user_text)
        self.conversation_history.append(f"[USER]: {user_text}")
        self.user_input.delete(0, tk.END)
        self.user_input.config(state=tk.DISABLED)
        threading.Thread(target=self.get_ai_response, args=(user_text,), daemon=True).start()

    def get_ai_response(self, user_text):
        """Sends conversation history and the latest message to the backend and appends the assistant response to history."""
        try:
            payload = {"history": self.conversation_history, "message": user_text}
            response = requests.post(API_URL, json=payload)
            ai_text = response.json().get("response", "Error: No response")
            self.after(0, self.add_message, "AI", ai_text)
            self.conversation_history.append(f"[ASSISTANT]: {ai_text}")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to connect: {str(e)}"))
        finally:
            self.after(0, lambda: self.user_input.config(state=tk.NORMAL))

    def clear_text(self):
        """Clears the text display."""
        self.text_display.delete("1.0", tk.END)

if __name__ == "__main__":
    import subprocess, time, requests
    backend_process = subprocess.Popen(["python", "backend.py"])
    print("Waiting for backend to start...")
    time.sleep(5)
    backend_ready = False
    for _ in range(10):
        try:
            r = requests.get("http://127.0.0.1:8000/chat")
            if r.status_code == 405:
                backend_ready = True
                print("Backend is ready!")
                break
        except requests.ConnectionError:
            print("Backend not ready yet, retrying...")
            time.sleep(2)
    if not backend_ready:
        print("Error: Backend failed to start. Check logs.")
        exit(1)
    app = ChatbotApp()
    app.mainloop()
    backend_process.terminate()
