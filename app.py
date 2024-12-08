import tkinter as tk
from tkinter import ttk, messagebox
import os


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Timer")
        self.root.geometry("400x600")
        self.root.config(bg="#2E2E2E")  # Dark background
        self.root.resizable(True, True)

        # Customize style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "TCombobox",
            fieldbackground="#2E2E2E",
            background="pink",
            foreground="white",
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#2E2E2E")],
            background=[("active", "#FF69B4")],
        )
        self.style.configure(
            "TButton",
            background="white",
            foreground="black",
            borderwidth=1,
            relief="flat",
        )
        self.style.map("TButton", background=[("active", "pink")])

        self.last_action_file = "last_action.txt"
        self.last_action = self.load_last_action()

        self.create_start_page()

    def load_last_action(self):
        if os.path.exists(self.last_action_file):
            with open(self.last_action_file, "r") as file:
                return file.read().strip()
        return "Shutdown"

    def save_last_action(self, action):
        with open(self.last_action_file, "w") as file:
            file.write(action)

    def create_start_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Set Timer",
            font=("Helvetica", 24, "bold"),
            fg="#FFFFFF",
            bg="#2E2E2E",
        ).pack(pady=20)

        # Time suggestion buttons
        suggested_times_frame = tk.Frame(self.root, bg="#2E2E2E")
        suggested_times_frame.pack(pady=10)

        for text, value in [("5 min", 300), ("30 min", 1800), ("1 hr", 3600)]:
            ttk.Button(
                suggested_times_frame,
                text=text,
                command=lambda v=value: self.set_suggested_time(v),
            ).pack(side=tk.LEFT, padx=10)

        # Dropdown for hours, minutes, seconds
        input_frame = tk.Frame(self.root, bg="#2E2E2E")
        input_frame.pack(pady=10)

        self.hours_var = tk.IntVar(value=0)
        self.minutes_var = tk.IntVar(value=0)
        self.seconds_var = tk.IntVar(value=0)

        self.create_time_input(input_frame, "Hours", self.hours_var, 24, 0)
        self.create_time_input(input_frame, "Minutes", self.minutes_var, 60, 1)
        self.create_time_input(input_frame, "Seconds", self.seconds_var, 60, 2)

        # Dropdown for action
        tk.Label(
            self.root,
            text="Action",
            font=("Helvetica", 14),
            fg="#FFFFFF",
            bg="#2E2E2E",
        ).pack(pady=10)

        self.action_var = tk.StringVar(value=self.last_action)
        action_order = ["Shutdown", "Restart", "Sleep"]
        action_order.remove(self.last_action)
        action_order.insert(0, self.last_action)

        action_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.action_var,
            font=("Helvetica", 12),
            width=15,
            state="readonly",
        )
        action_dropdown["values"] = action_order
        action_dropdown.pack()

        # Start Timer Button
        start_timer_button = ttk.Button(self.root, text="Start Timer", command=self.start_timer_ui)
        start_timer_button.pack(pady=30)

    def set_suggested_time(self, seconds):
        self.hours_var.set(seconds // 3600)
        self.minutes_var.set((seconds % 3600) // 60)
        self.seconds_var.set(seconds % 60)

    def create_time_input(self, frame, label_text, var, max_value, column):
        tk.Label(
            frame,
            text=label_text,
            font=("Helvetica", 14),
            fg="#FFFFFF",
            bg="#2E2E2E",
        ).grid(row=0, column=column, padx=10, pady=10)
        dropdown = ttk.Combobox(
            frame,
            textvariable=var,
            font=("Helvetica", 12),
            width=5,
            state="readonly",
        )
        dropdown["values"] = list(range(max_value))
        dropdown.grid(row=1, column=column, padx=10, pady=10)
        dropdown.configure(height=10)

    def start_timer_ui(self):
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        self.remaining_time = hours * 3600 + minutes * 60 + seconds

        if self.remaining_time <= 0:
            messagebox.showwarning("Invalid Time", "Please set a valid time.")
            return

        self.timer_action = self.action_var.get()
        self.save_last_action(self.timer_action)
        self.timer_running = True
        self.timer_paused = False
        self.create_timer_page()
        self.start_countdown()

    def create_timer_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Timer",
            font=("Helvetica", 24, "bold"),
            fg="#FFFFFF",
            bg="#2E2E2E",
        ).pack(pady=20)

        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="#2E2E2E", bd=0, highlightthickness=0)
        self.canvas.pack(pady=20)
        self.canvas.create_oval(50, 50, 250, 250, outline="gray", width=10)
        self.arc = self.canvas.create_arc(50, 50, 250, 250, start=90, extent=0, outline="pink", width=10, style="arc")

        self.timer_label = self.canvas.create_text(
            150, 150, text=self.format_time(self.remaining_time), font=("Helvetica", 32, "bold"), fill="white"
        )

        button_frame = tk.Frame(self.root, bg="#2E2E2E")
        button_frame.pack(pady=20, fill=tk.X)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.create_start_page)
        self.cancel_button.pack(side=tk.LEFT, padx=50)

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_resume_timer)
        self.pause_button.pack(side=tk.RIGHT, padx=50)

    def start_countdown(self):
        def countdown():
            if self.remaining_time > 0:
                if not self.timer_paused:
                    self.remaining_time -= 1
                    self.canvas.itemconfig(self.timer_label, text=self.format_time(self.remaining_time))
                    self.update_circular_progress()
                self.root.after(1000, countdown)
            else:
                self.execute_action()

        countdown()

    def update_circular_progress(self):
        total_time = self.hours_var.get() * 3600 + self.minutes_var.get() * 60 + self.seconds_var.get()
        progress = (self.remaining_time / total_time) * 360
        self.canvas.itemconfig(self.arc, extent=-progress)

    def pause_resume_timer(self):
        if self.timer_paused:
            self.timer_paused = False
            self.pause_button.config(text="Pause")
        else:
            self.timer_paused = True
            self.pause_button.config(text="Resume")

    def execute_action(self):
        try:
            if self.timer_action == "Shutdown":
                if os.name == "nt":
                    os.system("shutdown /s /t 0")
                else:
                    os.system("osascript -e 'tell app \"System Events\" to shut down'")
            elif self.timer_action == "Restart":
                if os.name == "nt":
                    os.system("shutdown /r /t 0")
                else:
                    os.system("osascript -e 'tell app \"System Events\" to restart'")
            elif self.timer_action == "Sleep":
                if os.name == "nt":
                    os.system("powercfg -h off")  # Ensure hibernation is disabled
                    os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
                else:
                    os.system("pmset displaysleepnow")

        except Exception as e:
            messagebox.showerror("Error", f"Error executing action: {e}")


    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()