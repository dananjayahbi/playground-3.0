import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("Simple Tkinter GUI")

# Create a label widget
label = tk.Label(window, text="Hello, Tkinter!")
label.pack() # Use pack layout manager to place the label in the window

# Run the Tkinter event loop
window.mainloop()