# This is a simple Python application that generates all possible permutations of numbers between 0 and 9, and displays them in a grid. 
# It also generates a heatmap showing the frequency of digits in different positions. 
# The application uses the NumPy library for optimization and the Tkinter library for the GUI. 
# The application consists of a main class called NumberCombinationsApp, which contains methods for generating permutations and heatmaps. 
# The application is run using the Tkinter mainloop.

import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as tb
import numpy as np
import matplotlib.pyplot as plt
from itertools import permutations
import threading
import math

class NumberCombinationsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Combination Generator")
        self.root.geometry("700x500")

        # ttkbootstrap theme
        self.style = tb.Style("darkly")  # Dark mode theme
        self.dark_mode = True

        # Header Label
        tb.Label(root, text="Enter Numbers (0-9, separated by commas)", font=("Arial", 12)).pack(pady=5)

        # Single Input Field
        self.entry = tb.Entry(root, width=50, font=("Arial", 12), justify="center")
        self.entry.pack(pady=5)

        # Generate Button
        tb.Button(root, text="Generate Combinations", command=self.start_permutation_thread, bootstyle="primary").pack(pady=10)

        # Heatmap Button
        tb.Button(root, text="Show Heatmap", command=self.generate_heatmap, bootstyle="info").pack(pady=5)

        # Dark Mode Toggle
        self.toggle_button = tb.Button(root, text="Toggle Light Mode", command=self.toggle_theme, bootstyle="warning")
        self.toggle_button.pack(pady=5)

        # Scrollable Frame for Grid
        self.frame_container = tb.Frame(root)
        self.frame_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.frame_container)
        self.scrollbar = ttk.Scrollbar(self.frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tb.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        if self.dark_mode:
            self.style.theme_use("flatly")  # Light mode
            self.toggle_button.config(text="Toggle Dark Mode")
        else:
            self.style.theme_use("darkly")  # Dark mode
            self.toggle_button.config(text="Toggle Light Mode")

        self.dark_mode = not self.dark_mode

    def start_permutation_thread(self):
        """Runs permutation generation in a separate thread to keep UI responsive"""
        threading.Thread(target=self.generate_combinations, daemon=True).start()

    def generate_combinations(self):
        """Generates and displays permutations using NumPy for optimization"""
        input_text = self.entry.get()
        numbers = input_text.replace(" ", "").split(",")

        # Validate numbers
        valid_numbers = []
        for num in numbers:
            if num.isdigit() and 0 <= int(num) <= 9:
                valid_numbers.append(int(num))
            else:
                messagebox.showerror("Input Error", "Please enter numbers between 0 and 9, separated by commas.")
                return

        if len(valid_numbers) == 0:
            messagebox.showerror("Input Error", "Please enter at least one number.")
            return

        # Generate all possible permutations using NumPy for performance
        num_array = np.array(valid_numbers)
        combinations = list(permutations(num_array, len(num_array)))

        # Clear previous grid
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Define grid layout (5 columns per row)
        columns = 5
        rows = math.ceil(len(combinations) / columns)

        for idx, combo in enumerate(combinations):
            combo_text = "".join(map(str, combo))  # Example: "12345"
            row, col = divmod(idx, columns)

            label = tb.Label(self.scrollable_frame, text=combo_text, borderwidth=1, relief="solid", width=10, font=("Arial", 10))
            label.grid(row=row, column=col, padx=5, pady=2)

    def generate_heatmap(self):
        """Generates a heatmap showing the frequency of digits in different positions"""
        input_text = self.entry.get()
        numbers = input_text.replace(" ", "").split(",")

        # Validate numbers
        valid_numbers = []
        for num in numbers:
            if num.isdigit() and 0 <= int(num) <= 9:
                valid_numbers.append(int(num))
            else:
                messagebox.showerror("Input Error", "Please enter numbers between 0 and 9, separated by commas.")
                return

        if len(valid_numbers) == 0:
            messagebox.showerror("Input Error", "Please enter at least one number.")
            return

        # Generate permutations
        num_array = np.array(valid_numbers)
        combinations = list(permutations(num_array, len(num_array)))

        # Create heatmap data (how often each number appears in each position)
        num_digits = len(valid_numbers)
        heatmap_data = np.zeros((10, num_digits))  # 10 rows (digits 0-9), columns = positions

        for combo in combinations:
            for pos, digit in enumerate(combo):
                heatmap_data[digit][pos] += 1  # Count occurrences of digits per position

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.imshow(heatmap_data, cmap="coolwarm", aspect="auto")

        ax.set_xticks(np.arange(num_digits))
        ax.set_xticklabels([f"Position {i+1}" for i in range(num_digits)])

        ax.set_yticks(np.arange(10))
        ax.set_yticklabels([str(i) for i in range(10)])

        plt.colorbar(cax, label="Frequency")
        plt.title("Digit Frequency Heatmap")
        plt.xlabel("Digit Position")
        plt.ylabel("Digit (0-9)")

        plt.show()

# Run the Tkinter Application
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = NumberCombinationsApp(root)
    root.mainloop()
