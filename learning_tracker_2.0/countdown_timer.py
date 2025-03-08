import os
import time
import json
import datetime
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class CountdownTimer:
    def __init__(self, app, parent, name, goal_seconds, test_mode=False):
        self.app = app  # Reference to the global TimerApp instance.
        self.parent = parent
        self.name = name
        self.goal_seconds = goal_seconds
        self.test_mode = test_mode
        self.running = False
        self.start_time = None
        self.update_job = None
        
        # State variables for persistence.
        self.remaining = goal_seconds
        self.daily_max_progress = 0  # Maximum progress achieved today (in seconds).
        self.goal_hit = False
        self.history = {}  # Dictionary mapping date string to progress (in seconds).
        
        # Determine file path for this timer (stored in the app's countdown folder).
        safe_name = self.name.replace(" ", "_")
        self.file_path = os.path.join(self.app.countdown_db_folder, f"countdown_{safe_name}.json")
        self.load_state()
        
        # Build UI.
        self.frame = ttk.Frame(self.parent, relief="groove", borderwidth=2)
        self.frame.pack(fill="x", padx=5, pady=5)
        
        self.name_label = ttk.Label(self.frame, text=self.name, font=("Helvetica", 12, "bold"))
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.time_label = ttk.Label(self.frame, text=self.format_time(self.remaining), font=("Helvetica", 12))
        self.time_label.grid(row=0, column=1, padx=5, pady=5)
        
        self.start_button = ttk.Button(self.frame, text="Start", command=self.start_timer, bootstyle=SUCCESS, width=8)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.pause_button = ttk.Button(self.frame, text="Pause", command=self.pause_timer, bootstyle=WARNING, width=8)
        self.pause_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.reset_button = ttk.Button(self.frame, text="Reset", command=self.reset_timer, bootstyle=DANGER, width=8)
        self.reset_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.delete_button = ttk.Button(self.frame, text="Delete", command=self.delete_timer, bootstyle=OUTLINE, width=8)
        self.delete_button.grid(row=0, column=5, padx=5, pady=5)
    
    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            # Auto-start the global timer if it isn't running.
            if not self.app.running:
                self.app.start_timer()
            self.update_timer()
            self.save_state()
    
    def pause_timer(self):
        if self.running:
            self.running = False
            if self.update_job is not None:
                try:
                    self.frame.after_cancel(self.update_job)
                except:
                    pass
                self.update_job = None
            elapsed = time.time() - self.start_time
            self.remaining = max(0, self.remaining - elapsed)
            self.time_label.config(text=self.format_time(self.remaining))
            progress = self.goal_seconds - self.remaining
            if progress > self.daily_max_progress:
                self.daily_max_progress = progress
            self.save_state()
    
    def reset_timer(self):
        self.running = False
        if self.update_job is not None:
            try:
                self.frame.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
        self.remaining = self.goal_seconds
        self.daily_max_progress = 0
        self.goal_hit = False
        self.time_label.config(text=self.format_time(self.remaining))
        self.save_state()
    
    def update_timer(self):
        if self.running:
            elapsed = time.time() - self.start_time
            current_remaining = max(0, self.remaining - elapsed)
            self.time_label.config(text=self.format_time(current_remaining))
            progress = self.goal_seconds - current_remaining
            
            if progress > self.daily_max_progress:
                self.daily_max_progress = progress
            
            if current_remaining <= 0 and not self.goal_hit:
                # Goal reached
                self.running = False
                self.goal_hit = True
                self.daily_max_progress = self.goal_seconds
                messagebox.showinfo("Timer Finished", f"{self.name} countdown has finished and goal achieved!")
                self.reset_timer()
                self.save_state()
                return
            else:
                self.update_job = self.frame.after(100, self.update_timer)
            self.save_state()
    
    def reset_at_midnight(self):
        today_str = datetime.date.today().isoformat()
        self.history[today_str] = self.daily_max_progress
        self.reset_timer()
        self.save_state()
    
    def delete_timer(self):
        answer = messagebox.askyesno("Delete Timer", f"Are you sure you want to delete timer: {self.name}?")
        if answer:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            self.frame.destroy()
            if self in self.app.countdown_timers:
                self.app.countdown_timers.remove(self)
    
    def stop_update_loop(self):
        # If the timer is running, update the remaining time before stopping.
        if self.running and self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.remaining = max(0, self.remaining - elapsed)
        if self.update_job is not None:
            try:
                self.frame.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
        self.running = False
    
    def save_state(self):
        state = {
            "name": self.name,
            "goal_seconds": self.goal_seconds,
            "remaining": (
                max(0, self.remaining - (time.time() - self.start_time))
                if self.running and self.start_time
                else self.remaining
            ),
            "daily_max_progress": self.daily_max_progress,
            "goal_hit": self.goal_hit,
            "history": self.history,
            "test_mode": self.test_mode
        }
        with open(self.file_path, "w") as f:
            json.dump(state, f)
    
    def load_state(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    state = json.load(f)
                    self.remaining = state.get("remaining", self.goal_seconds)
                    self.daily_max_progress = state.get("daily_max_progress", 0)
                    self.goal_hit = state.get("goal_hit", False)
                    self.history = state.get("history", {})
                except Exception:
                    self.remaining = self.goal_seconds
                    self.daily_max_progress = 0
                    self.goal_hit = False
                    self.history = {}
        else:
            self.remaining = self.goal_seconds
            self.daily_max_progress = 0
            self.goal_hit = False
            self.history = {}
    
    def get_history(self):
        return self.history
    
    def format_time(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    
    @staticmethod
    def load_from_file(app, parent, filepath, test_mode=False):
        try:
            with open(filepath, "r") as f:
                state = json.load(f)
            name = state.get("name")
            goal_seconds = state.get("goal_seconds")
            timer = CountdownTimer(app, parent, name, goal_seconds, test_mode)
            timer.remaining = state.get("remaining", goal_seconds)
            timer.daily_max_progress = state.get("daily_max_progress", 0)
            timer.goal_hit = state.get("goal_hit", False)
            timer.history = state.get("history", {})
            return timer
        except Exception as e:
            print(f"Failed to load countdown timer from {filepath}: {e}")
            return None
