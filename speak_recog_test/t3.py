import tkinter as tk
import torch
import whisper
import pyaudio
import wave
import threading
import os
from tkinter import filedialog
from pydub import AudioSegment

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Speech Recognition")
        self.root.geometry("500x300")

        self.is_recording = False
        self.audio_file = "recorded_audio.wav"
        self.converted_audio = "converted_audio.wav"  # Converted file for non-WAV formats
        self.model = None

        # UI Elements
        self.record_btn = tk.Button(root, text="🎤 Start Recording", command=self.toggle_recording, bg="lightblue", font=("Arial", 14))
        self.record_btn.pack(pady=10)

        self.upload_btn = tk.Button(root, text="📂 Upload Audio File", command=self.upload_audio, bg="lightgreen", font=("Arial", 14))
        self.upload_btn.pack(pady=10)

        self.text_display = tk.Text(root, height=8, width=50, font=("Arial", 12))
        self.text_display.pack(pady=10)

        self.clear_btn = tk.Button(root, text="❌ Clear", command=self.clear_text, bg="lightcoral", font=("Arial", 14))
        self.clear_btn.pack(pady=10)

        # Load Whisper Model Asynchronously
        threading.Thread(target=self.load_model, daemon=True).start()

    def load_model(self):
        """Loads the Whisper model from the local models/ folder."""
        self.text_display.insert(tk.END, "Loading Whisper model... Please wait.\n")
        try:
            model_path = os.path.join("models", "base.pt")  # Path to the locally stored model
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if not os.path.exists(model_path):
                self.text_display.insert(tk.END, "Error: Model file not found in models/ folder.\n")
                return

            self.model = whisper.load_model(model_path, device=device)
            self.text_display.insert(tk.END, f"Whisper model loaded successfully from models/ on {device.upper()}!\n")
        except Exception as e:
            self.text_display.insert(tk.END, f"Error loading model: {e}\n")

    def toggle_recording(self):
        """Toggles recording on first click, stops and transcribes on second click."""
        if not self.is_recording:
            self.is_recording = True
            self.record_btn.config(text="🛑 Stop Recording", bg="red")
            self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.recording_thread.start()
        else:
            self.is_recording = False
            self.recording_thread.join()
            self.record_btn.config(text="🎤 Start Recording", bg="lightblue")

            if os.path.exists(self.audio_file):
                text = self.transcribe_audio(self.audio_file)
                self.text_display.insert(tk.END, text + "\n" if text else "I couldn't understand. Try again.\n")
            else:
                self.text_display.insert(tk.END, "Error: Audio file not saved properly.\n")

    def record_audio(self):
        """Records directly at 16kHz, 16-bit Mono and saves it as a WAV file."""
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

            # Save as WAV file
            with wave.open(self.audio_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(mic.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

        except Exception as e:
            self.text_display.insert(tk.END, f"Recording error: {e}\n")

    def upload_audio(self):
        """Allows the user to select an audio file and converts if needed."""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.m4a")])
        if not file_path:
            return  # User canceled

        self.text_display.insert(tk.END, f"Processing file: {file_path}\n")

        # Convert to WAV if needed
        if file_path.endswith(".wav"):
            self.text_display.insert(tk.END, "Using WAV file as is.\n")
            final_audio = file_path
        else:
            self.text_display.insert(tk.END, "Converting audio to WAV...\n")
            final_audio = self.convert_audio(file_path)

        # Transcribe the final audio file
        text = self.transcribe_audio(final_audio)
        self.text_display.insert(tk.END, text + "\n" if text else "I couldn't understand. Try again.\n")

    def convert_audio(self, input_path):
        """Converts MP3 or M4A files to WAV format."""
        try:
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)  # Convert to Mono, 16kHz, 16-bit
            audio.export(self.converted_audio, format="wav")
            return self.converted_audio
        except Exception as e:
            self.text_display.insert(tk.END, f"Conversion error: {e}\n")
            return None

    def transcribe_audio(self, file_path):
        """Transcribes speech from an audio file using Whisper."""
        if self.model is None:
            return "Error: Whisper model not loaded."

        try:
            result = self.model.transcribe(file_path)
            return result["text"].strip()
        except Exception as e:
            return f"Transcription error: {e}"

    def clear_text(self):
        """Clears the text display."""
        self.text_display.delete("1.0", tk.END)

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()
