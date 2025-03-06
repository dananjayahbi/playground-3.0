import cv2
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import threading
import queue
import time
import torch
import numpy as np

# Variable Zone - Adjust these parameters as needed
FRAME_WIDTH = 320              # Width of the frame (lower for less computation)
FRAME_HEIGHT = 240             # Height of the frame (lower for less computation)
SMOOTHING_ALPHA = 0.5          # Smoothing factor for mouse movement (0 to 1)
SCALING_FACTOR = 4.0           # Mouse movement scaling
TAP_DISTANCE_THRESHOLD = 30    # Distance threshold for gesture detection
DOUBLE_TAP_INTERVAL = 0.5      # Time (seconds) to detect double tap
GUI_UPDATE_INTERVAL = 50       # GUI update interval (milliseconds)
FRAME_SKIP = 1                 # Process every nth frame (1 = no skip)

class HandMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Mouse Control")

        # Set up video capture
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise Exception("Could not open webcam")

        # Initialize PyTorch hand detection model (replace with your model)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Placeholder: Load your PyTorch model here
        # Example: self.model = torch.load('path/to/hand_model.pt').to(self.device)
        self.model = DummyHandModel().to(self.device)  # Dummy model for demonstration
        self.model.eval()

        # Create GUI elements
        self.label = tk.Label(root)
        self.label.pack()
        self.instructions = tk.Label(
            root,
            text="Gestures: Move - Thumb+Index, Click - Thumb+Middle, Double Click - Thumb+Middle Twice, Right Click - Thumb+Pinky"
        )
        self.instructions.pack()
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack()

        # Mouse control variables
        self.gesture_active = False
        self.smoothed_x = None
        self.smoothed_y = None
        self.previous_smoothed_x = None
        self.previous_smoothed_y = None
        self.last_tap_time = 0
        self.tap_count = 0

        # Frame queue for GUI updates
        self.frame_queue = queue.Queue(maxsize=1)
        self.frame_counter = 0

        # Start worker thread for frame processing
        self.worker_thread = threading.Thread(target=self.process_frames, daemon=True)
        self.worker_thread.start()

        # Start GUI update loop
        self.update_gui()

    def process_frames(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_counter += 1
            if self.frame_counter % FRAME_SKIP != 0:
                continue  # Skip frames if FRAME_SKIP > 1

            # Preprocess frame
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect hand landmarks with PyTorch on CUDA
            landmarks = self.detect_hand_landmarks(frame_rgb)
            if landmarks is not None:
                # Draw landmarks (for visualization)
                for x, y in landmarks:
                    cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)

                # Gesture detection using landmark coordinates
                thumb_tip = landmarks[0]  # Example indices; adjust based on your model
                index_tip = landmarks[1]
                middle_tip = landmarks[2]
                pinky_tip = landmarks[3]

                thumb_index_dist = self.calculate_distance(thumb_tip, index_tip)
                thumb_middle_dist = self.calculate_distance(thumb_tip, middle_tip)
                thumb_pinky_dist = self.calculate_distance(thumb_tip, pinky_tip)

                if thumb_index_dist < TAP_DISTANCE_THRESHOLD:
                    self.handle_move_gesture(landmarks)
                elif thumb_middle_dist < TAP_DISTANCE_THRESHOLD:
                    self.handle_click_gesture()
                elif thumb_pinky_dist < TAP_DISTANCE_THRESHOLD:
                    pyautogui.click(button='right')

            # Update GUI occasionally
            if self.frame_queue.empty():
                self.frame_queue.put(frame.copy())

    def detect_hand_landmarks(self, frame_rgb):
        """Detect hand landmarks using a PyTorch model on CUDA."""
        # Convert frame to tensor and move to GPU
        frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).unsqueeze(0).float().to(self.device) / 255.0
        with torch.no_grad():
            output = self.model(frame_tensor)
        # Post-process output (adjust based on your model's output format)
        # Example: Assume output is [batch, num_landmarks, 2] for x, y coordinates
        landmarks = output.squeeze(0).cpu().numpy() * [FRAME_WIDTH, FRAME_HEIGHT]  # Scale to frame size
        return landmarks if len(landmarks) > 0 else None

    def update_gui(self):
        try:
            frame = self.frame_queue.get_nowait()
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)
            self.label.config(image=photo)
            self.label.image = photo
        except queue.Empty:
            pass
        self.root.after(GUI_UPDATE_INTERVAL, self.update_gui)

    def calculate_distance(self, point1, point2):
        return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

    def handle_move_gesture(self, landmarks):
        index_tip = landmarks[1]  # Adjust index based on your model
        current_x, current_y = index_tip

        if self.smoothed_x is None:
            self.smoothed_x = current_x
            self.smoothed_y = current_y
        else:
            self.smoothed_x = SMOOTHING_ALPHA * current_x + (1 - SMOOTHING_ALPHA) * self.smoothed_x
            self.smoothed_y = SMOOTHING_ALPHA * current_y + (1 - SMOOTHING_ALPHA) * self.smoothed_y

        if self.gesture_active:
            delta_x = self.smoothed_x - self.previous_smoothed_x
            delta_y = self.smoothed_y - self.previous_smoothed_y
            dx = -SCALING_FACTOR * delta_x
            dy = SCALING_FACTOR * delta_y
            pyautogui.moveRel(dx, dy)

        self.gesture_active = True
        self.previous_smoothed_x = self.smoothed_x
        self.previous_smoothed_y = self.smoothed_y

    def handle_click_gesture(self):
        current_time = time.time()
        if current_time - self.last_tap_time < DOUBLE_TAP_INTERVAL:
            self.tap_count += 1
        else:
            self.tap_count = 1

        self.last_tap_time = current_time
        if self.tap_count == 1:
            pyautogui.click()
        elif self.tap_count == 2:
            pyautogui.doubleClick()
            self.tap_count = 0

    def on_closing(self):
        self.cap.release()
        self.root.destroy()

# Dummy model for demonstration (replace with your actual PyTorch model)
class DummyHandModel(torch.nn.Module):
    def __init__(self):
        super(DummyHandModel, self).__init__()
        self.conv = torch.nn.Conv2d(3, 4, kernel_size=3, padding=1)
        self.fc = torch.nn.Linear(4 * FRAME_HEIGHT * FRAME_WIDTH, 8)  # 4 landmarks * 2 (x, y)

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x.view(-1, 4, 2)  # [batch, 4 landmarks, 2 coords]

if __name__ == "__main__":
    root = tk.Tk()
    app = HandMouseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()