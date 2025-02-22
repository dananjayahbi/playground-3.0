import tkinter as tk
from tkinter import filedialog, messagebox
from vosk import Model, KaldiRecognizer
import wave
import json
import os

# Set FFmpeg path dynamically
from pydub.utils import which
os.environ["PATH"] += os.pathsep + os.path.abspath("ffmpeg/bin/")

# Now import pydub
from pydub import AudioSegment

# Initialize Vosk model
vosk_model_path = "models/vosk-model-small-en-us-0.15"
if not os.path.exists(vosk_model_path):
    messagebox.showerror("Error", "Vosk model not found! Make sure it's in the models/ directory.")
    exit(1)

model = Model(vosk_model_path)

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vosk MP3/WAV Audio Transcription")
        self.root.geometry("500x300")

        # Upload File Button
        self.upload_btn = tk.Button(root, text="📂 Upload Audio File", command=self.upload_file, bg="lightblue", font=("Arial", 14))
        self.upload_btn.pack(pady=10)

        # Text Display
        self.text_display = tk.Text(root, height=8, width=50, font=("Arial", 12))
        self.text_display.pack(pady=10)

        # Clear Button
        self.clear_btn = tk.Button(root, text="❌ Clear", command=self.clear_text, bg="lightcoral", font=("Arial", 14))
        self.clear_btn.pack(pady=10)

    def upload_file(self):
        """Opens file dialog to upload an MP3 or WAV file and transcribe it."""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if not file_path:
            return

        try:
            self.text_display.insert(tk.END, "Processing audio file...\n")
            self.root.update_idletasks()

            # Convert MP3 to WAV if needed
            if file_path.endswith(".mp3"):
                wav_path = self.convert_mp3_to_wav(file_path)
            else:
                wav_path = file_path  # Already WAV

            # Transcribe the WAV file
            text = self.transcribe_audio(wav_path)

            if text:
                self.text_display.insert(tk.END, text + "\n")
            else:
                self.text_display.insert(tk.END, "I couldn't understand. Please try again.\n")

            # Delete temporary WAV file (if created)
            if file_path.endswith(".mp3") and os.path.exists(wav_path):
                os.remove(wav_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}")

    def convert_mp3_to_wav(self, mp3_path):
        """Converts an MP3 file to WAV format compatible with Vosk."""
        audio = AudioSegment.from_mp3(mp3_path)
        wav_path = mp3_path.replace(".mp3", ".wav")
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)  # Convert to Mono, 16kHz, 16-bit
        audio.export(wav_path, format="wav")
        return wav_path

    def transcribe_audio(self, file_path):
        """Transcribes speech from an audio file using Vosk."""
        wf = wave.open(file_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            messagebox.showerror("Error", "Audio file must be Mono, 16-bit, 16kHz. Conversion failed.")
            return ""

        recognizer = KaldiRecognizer(model, 16000)
        while True:
            data = wf.readframes(4096)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult())["text"]
        return result.strip()

    def clear_text(self):
        """Clears the text display."""
        self.text_display.delete("1.0", tk.END)

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()
