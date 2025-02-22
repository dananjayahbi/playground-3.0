import tkinter as tk
import whisper
import pyaudio
import wave
import threading
import os

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Speech Recognition")
        self.root.geometry("500x300")

        self.is_recording = False
        self.audio_file = "recorded_audio.wav"
        self.model = None

        # UI Elements
        self.record_btn = tk.Button(root, text="🎤 Start Recording", command=self.toggle_recording, bg="lightblue", font=("Arial", 14))
        self.record_btn.pack(pady=10)

        self.text_display = tk.Text(root, height=8, width=50, font=("Arial", 12))
        self.text_display.pack(pady=10)

        self.clear_btn = tk.Button(root, text="❌ Clear", command=self.clear_text, bg="lightcoral", font=("Arial", 14))
        self.clear_btn.pack(pady=10)

        # Load Whisper Model Asynchronously
        threading.Thread(target=self.load_model, daemon=True).start()

    def load_model(self):
        """Loads the Whisper model asynchronously, using GPU if available."""
        self.text_display.insert(tk.END, "Loading Whisper model... Please wait.\n")
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = whisper.load_model("small", device=device)  # Use GPU if available
            self.text_display.insert(tk.END, f"Whisper model loaded successfully on {device.upper()}!\n")
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
