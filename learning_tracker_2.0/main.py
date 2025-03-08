import ttkbootstrap as ttk
from timer_app import TimerApp

def main():
    root = ttk.Window(themename="flatly")
    root.resizable(False, False)
    app = TimerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
