import os
import time
import json
import datetime
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from countdown_timer import CountdownTimer

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Learning Hours Tracker")
        self.master.attributes("-topmost", True)
        self.master.resizable(False, False)
        self.style = ttk.Style("flatly")
        
        # -------------------------------
        # Folder structure for DB and reports
        self.db_folder = "db"
        self.report_folder = "reports"
        os.makedirs(self.db_folder, exist_ok=True)
        os.makedirs(self.report_folder, exist_ok=True)
        
        # Countdown timers folder
        self.countdown_db_folder = os.path.join(self.db_folder, "countdowns")
        os.makedirs(self.countdown_db_folder, exist_ok=True)
        
        self.history_file = os.path.join(self.db_folder, "history.json")
        self.session_file = os.path.join(self.db_folder, "session.json")
        # -------------------------------
        
        # ===============================
        # TEST_MODE: Set to True for testing (30 sec) or False for production (24 hrs).
        self.TEST_MODE = False  
        if self.TEST_MODE:
            self.session_interval = 30  # seconds for testing
        else:
            self.session_interval = 24 * 3600  # 24 hours
        # ===============================
        
        # UI Setup
        self.setup_ui()
        
        # Global timer variables
        self.running = False
        self.start_time = None
        self.elapsed_time = 0.0
        self.last_start_time = None
        self.update_job = None
        self.check_session_job = None
        self.laps = []
        
        # List to hold individual countdown timers
        self.countdown_timers = []
        
        # Load persisted data
        self.load_history()
        self.load_session()
        self.load_countdown_timers()
        
        if not self.TEST_MODE:
            self.daily_date = datetime.date.today()
        if not hasattr(self, 'session_init_time'):
            self.session_init_time = time.time()
        
        # Start background session check
        self.check_session()
    
    def setup_ui(self):
        """
        Creates a container Frame that centers the global timer portion horizontally,
        so that when we add countdown timers below, the top part remains centered.
        """
        # Make the root window expandable
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        
        # Create a container to hold everything
        self.container = ttk.Frame(self.master)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)  # So it can center contents
        
        # ------------------ GLOBAL TIMER FRAME ------------------
        self.global_frame = ttk.Frame(self.container)
        self.global_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        # Big timer display
        self.time_label = ttk.Label(self.global_frame, text="00:00:00", font=("Helvetica", 40))
        self.time_label.pack(pady=10)
        
        # Frame for the control buttons
        self.button_frame = ttk.Frame(self.global_frame)
        self.button_frame.pack(pady=5)
        
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_timer, bootstyle=SUCCESS)
        self.start_button.grid(row=0, column=0, padx=5)
        self.pause_button = ttk.Button(self.button_frame, text="Pause", command=self.pause_timer, bootstyle=WARNING)
        self.pause_button.grid(row=0, column=1, padx=5)
        self.lap_button = ttk.Button(self.button_frame, text="Lap", command=self.lap_time, bootstyle=INFO)
        self.lap_button.grid(row=0, column=2, padx=5)
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_timer, bootstyle=DANGER)
        self.reset_button.grid(row=0, column=3, padx=5)
        
        # Lap listbox
        self.lap_listbox = tk.Listbox(self.global_frame, width=50)
        self.lap_listbox.pack(pady=10)
        
        # Show History button (below global frame)
        self.history_button = ttk.Button(self.container, text="Show History", command=self.show_history, bootstyle=PRIMARY)
        self.history_button.grid(row=1, column=0, pady=10, sticky="n")
        
        # ------------------ COUNTDOWN TIMERS FRAME ------------------
        self.countdown_frame = ttk.LabelFrame(self.container, text="Countdown Timers")
        self.countdown_frame.grid(row=2, column=0, padx=10, pady=10, sticky="n")
        self.countdown_frame.columnconfigure(0, weight=1)
        
        # "Add Countdown Timer" button
        self.add_countdown_button = ttk.Button(self.countdown_frame, text="Add Countdown Timer", command=self.add_countdown_timer, bootstyle=SUCCESS)
        self.add_countdown_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Frame to list all countdown timers
        self.timers_list_frame = ttk.Frame(self.countdown_frame)
        self.timers_list_frame.grid(row=1, column=0, sticky="ew")
    
    def add_countdown_timer(self):
        def create_timer():
            name = name_entry.get().strip()
            duration_str = duration_entry.get().strip()
            try:
                duration_hours = float(duration_str)
                duration_seconds = int(duration_hours * 3600)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for duration in hours.")
                return
            
            timer = CountdownTimer(self, self.timers_list_frame, name, duration_seconds, self.TEST_MODE)
            self.countdown_timers.append(timer)
            timer.save_state()  # Save initial state
            top.destroy()
        
        top = tk.Toplevel(self.master)
        top.title("Add Countdown Timer")
        top.resizable(False, False)
        ttk.Label(top, text="Timer Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(top)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(top, text="Duration (hours):").grid(row=1, column=0, padx=5, pady=5)
        duration_entry = ttk.Entry(top)
        duration_entry.grid(row=1, column=1, padx=5, pady=5)
        create_btn = ttk.Button(top, text="Create", command=create_timer, bootstyle=SUCCESS)
        create_btn.grid(row=2, column=0, columnspan=2, pady=10)
    
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                try:
                    self.history = json.load(f)
                except Exception:
                    self.history = {}
        else:
            self.history = {}
    
    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f)
    
    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                try:
                    session = json.load(f)
                except Exception:
                    session = None
            if session:
                if self.TEST_MODE:
                    saved_init = session.get("session_init_time", time.time())
                    if time.time() - saved_init < self.session_interval:
                        self.session_init_time = saved_init
                        self.daily_seconds = session.get("daily_seconds", 0.0)
                        self.running = session.get("running", False)
                        self.elapsed_time = session.get("elapsed_time", 0.0)
                        self.last_start_time = session.get("last_start_time", None)
                        self.laps = session.get("laps", [])
                        self.time_label.config(text=self.format_time(self.elapsed_time))
                        for lap in self.laps:
                            self.lap_listbox.insert(tk.END, self.format_time(lap))
                        if self.running and self.last_start_time is not None:
                            additional = time.time() - self.last_start_time
                            self.elapsed_time += additional
                            self.start_time = time.time() - self.elapsed_time
                            self.last_start_time = time.time()
                            self.update_timer()
                    else:
                        self.finalize_session(
                            datetime.datetime.fromtimestamp(saved_init).strftime("%Y-%m-%d %H:%M:%S"),
                            session.get("daily_seconds", 0.0)
                        )
                        self.reset_for_new_session()
                else:
                    saved_date = datetime.date.fromisoformat(session.get("daily_date", "1970-01-01"))
                    if saved_date == datetime.date.today():
                        self.daily_date = saved_date
                        self.daily_seconds = session.get("daily_seconds", 0.0)
                        self.running = session.get("running", False)
                        self.elapsed_time = session.get("elapsed_time", 0.0)
                        self.last_start_time = session.get("last_start_time", None)
                        self.laps = session.get("laps", [])
                        self.time_label.config(text=self.format_time(self.elapsed_time))
                        for lap in self.laps:
                            self.lap_listbox.insert(tk.END, self.format_time(lap))
                        if self.running and self.last_start_time is not None:
                            additional = time.time() - self.last_start_time
                            self.elapsed_time += additional
                            self.start_time = time.time() - self.elapsed_time
                            self.last_start_time = time.time()
                            self.update_timer()
                    else:
                        prev_seconds = session.get("daily_seconds", 0.0)
                        date_str = saved_date.isoformat()
                        if date_str in self.history:
                            self.history[date_str] += prev_seconds
                        else:
                            self.history[date_str] = prev_seconds
                        self.save_history()
                        self.generate_report(date_str, prev_seconds)
                        self.daily_date = datetime.date.today()
                        self.daily_seconds = 0.0
                        self.running = False
                        self.elapsed_time = 0.0
                        self.last_start_time = None
                        self.laps = []
                        self.time_label.config(text="00:00:00")
            else:
                self.init_new_session()
        else:
            self.init_new_session()
    
    def load_countdown_timers(self):
        for filename in os.listdir(self.countdown_db_folder):
            if filename.endswith(".json"):
                filepath = os.path.join(self.countdown_db_folder, filename)
                timer = CountdownTimer.load_from_file(self, self.timers_list_frame, filepath, self.TEST_MODE)
                if timer:
                    self.countdown_timers.append(timer)
    
    def init_new_session(self):
        if not self.TEST_MODE:
            self.daily_date = datetime.date.today()
        self.session_init_time = time.time()
        self.daily_seconds = 0.0
        self.running = False
        self.elapsed_time = 0.0
        self.last_start_time = None
        self.laps = []
    
    def save_session(self):
        session = {
            "daily_date": datetime.date.today().isoformat() if not self.TEST_MODE else "",
            "daily_seconds": self.daily_seconds,
            "running": self.running,
            "elapsed_time": self.elapsed_time,
            "last_start_time": self.last_start_time,
            "laps": self.laps,
            "session_init_time": self.session_init_time
        }
        with open(self.session_file, "w") as f:
            json.dump(session, f)
    
    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.last_start_time = time.time()
            self.update_timer()
            self.save_session()
    
    def pause_timer(self):
        if self.running:
            self.running = False
            if self.update_job is not None:
                try:
                    self.master.after_cancel(self.update_job)
                except:
                    pass
                self.update_job = None
            self.elapsed_time = time.time() - self.start_time
            self.daily_seconds += self.elapsed_time
            self.save_session()
    
    def reset_timer(self):
        self.running = False
        if self.update_job is not None:
            try:
                self.master.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
        self.start_time = None
        self.elapsed_time = 0.0
        self.last_start_time = None
        self.time_label.config(text="00:00:00")
        self.lap_listbox.delete(0, tk.END)
        self.laps = []
        self.save_session()
    
    def lap_time(self):
        if self.running:
            current_lap = time.time() - self.start_time
            self.laps.append(current_lap)
            formatted = self.format_time(current_lap)
            self.lap_listbox.insert(tk.END, formatted)
            self.save_session()
    
    def update_timer(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.time_label.config(text=self.format_time(self.elapsed_time))
            self.save_session()
            self.update_job = self.master.after(100, self.update_timer)
    
    def format_time(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    
    def check_session(self):
        if self.TEST_MODE:
            if time.time() - self.session_init_time >= self.session_interval:
                was_running = self.running
                if self.running and self.start_time is not None:
                    final_time = self.session_init_time + self.session_interval
                    elapsed_before_threshold = final_time - self.start_time
                    self.daily_seconds += max(0, elapsed_before_threshold)
                test_date_str = datetime.datetime.fromtimestamp(self.session_init_time).strftime("%Y-%m-%d %H:%M:%S")
                self.finalize_session(test_date_str, self.daily_seconds)
                self.reset_for_new_session()
                if was_running:
                    self.running = True
                    self.start_time = time.time()
                    self.last_start_time = time.time()
                    self.update_timer()
        else:
            today = datetime.date.today()
            if today != self.daily_date:
                was_running = self.running
                if self.running and self.start_time is not None:
                    prev_day_midnight = datetime.datetime.combine(self.daily_date + datetime.timedelta(days=1), datetime.time.min)
                    elapsed_before_midnight = prev_day_midnight.timestamp() - self.start_time
                    self.daily_seconds += max(0, elapsed_before_midnight)
                date_str = self.daily_date.isoformat()
                if date_str in self.history:
                    self.history[date_str] += self.daily_seconds
                else:
                    self.history[date_str] = self.daily_seconds
                self.save_history()
                self.generate_report(date_str, self.daily_seconds)
                # Reset for new day
                self.daily_date = today
                self.daily_seconds = 0.0
                self.elapsed_time = 0.0
                self.running = False
                self.last_start_time = None
                self.laps = []
                self.time_label.config(text="00:00:00")
                self.save_session()
                # Reset all countdown timers at midnight
                for timer in self.countdown_timers:
                    timer.reset_at_midnight()
                if was_running:
                    self.running = True
                    self.start_time = time.time()
                    self.last_start_time = time.time()
                    self.update_timer()
        self.check_session_job = self.master.after(1000, self.check_session)
    
    def finalize_session(self, session_label, seconds):
        if session_label in self.history:
            self.history[session_label] += seconds
        else:
            self.history[session_label] = seconds
        self.save_history()
        self.generate_report(session_label, seconds)
    
    def reset_for_new_session(self):
        self.session_init_time = time.time()
        self.daily_seconds = 0.0
        self.elapsed_time = 0.0
        self.running = False
        self.last_start_time = None
        self.laps = []
        self.time_label.config(text="00:00:00")
        self.lap_listbox.delete(0, tk.END)
        self.save_session()
    
    def generate_report(self, date_str, seconds):
        hours = seconds / 3600
        report = f"Date: {date_str}\nLearning Hours: {hours:.2f}\nTotal Seconds: {seconds:.0f}"
        safe_date_str = date_str.replace(":", "-")
        report_file = os.path.join(self.report_folder, f"report_{safe_date_str}.txt")
        with open(report_file, "w") as f:
            f.write(report)
        print("Report generated:", report_file)
        self.manage_reports()
    
    def manage_reports(self):
        files = [os.path.join(self.report_folder, f) for f in os.listdir(self.report_folder)
                 if f.startswith("report_") and f.endswith(".txt")]
        if len(files) > 5:
            files.sort(key=lambda x: os.path.getctime(x))
            for f in files[:len(files) - 5]:
                os.remove(f)
                print("Deleted old report:", f)
    
    def show_history(self):
        history_window = tk.Toplevel(self.master)
        history_window.title("Learning Hours History")
        history_window.resizable(False, False)
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Global history line
        if self.history:
            dates = []
            values = []
            for key in self.history.keys():
                try:
                    dt = datetime.datetime.fromisoformat(key)
                    dates.append(dt)
                    values.append(self.history[key] / 3600)
                except Exception:
                    continue
            if dates:
                ax.plot_date(dates, values, '-o', label="Global Learning Hours")
        
        # Countdown timers history
        for timer in self.countdown_timers:
            t_history = timer.get_history()
            if t_history:
                dates = []
                values = []
                for key in t_history.keys():
                    try:
                        dt = datetime.datetime.fromisoformat(key)
                        dates.append(dt)
                        values.append(t_history[key] / 3600)
                    except Exception:
                        continue
                if dates:
                    ax.plot_date(dates, values, '-o', label=f"Countdown: {timer.name}")
        
        ax.set_xlabel("Date")
        ax.set_ylabel("Hours")
        ax.set_title("History Overview")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.legend()
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=history_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def on_closing(self):
        # 1) Cancel the global timer update callback if scheduled
        if self.update_job is not None:
            try:
                self.master.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
        
        # 2) Cancel the session check callback
        if self.check_session_job is not None:
            try:
                self.master.after_cancel(self.check_session_job)
            except:
                pass
            self.check_session_job = None
        
        # 3) If the global timer is running, stop it and record final time
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.daily_seconds += self.elapsed_time
            self.running = False
        self.save_session()
        
        # 4) Cancel each countdown timer's update loop and save them
        for timer in self.countdown_timers:
            timer.stop_update_loop()
            timer.save_state()
        
        # 5) Quit the Tk mainloop and destroy the window
        self.master.quit()       # stops the main event loop
        self.master.destroy()    # closes the window completely
