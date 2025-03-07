import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import random

TASK_FILE = "memory_schedule_tasks.json"

if os.path.exists(TASK_FILE):
    with open(TASK_FILE, "r") as file:
        tasks = json.load(file)
else:
    tasks = {}

def save_tasks():
    """Save tasks to the TASK_FILE in JSON format."""
    with open(TASK_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

QUOTES = [
    "The future belongs to those who prepare for it today.",
    "Small progress is still progress.",
    "Every day is a chance to learn something new.",
    "Success is the sum of small efforts, repeated daily.",
    "Consistency is the key to mastery.",
]

SCHEDULE_INTERVALS = [0, 1, 3, 6, 13, 27, 55, 111, 223, 364]

class CalendarApp:
    def __init__(self, root):
        """Initialize the CalendarApp with the root window, set up UI, and render the calendar."""
        self.root = root
        self.root.title("Memory Schedule Calendar")
        self.root.geometry("900x700")

        self.current_date = datetime.now()
        self.selected_date = self.current_date

        self.create_ui()
        self.render_calendar()

    def create_ui(self):
        """Create the user interface components."""
        self.header_frame = tk.Frame(self.root, bg="#4CAF50")
        self.header_frame.pack(fill=tk.X)

        self.quote_label = tk.Label(
            self.header_frame,
            text=random.choice(QUOTES),
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#4CAF50",
            pady=10,
        )
        self.quote_label.pack()

        self.navigation_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.navigation_frame.pack(fill=tk.X)

        self.prev_button = tk.Button(
            self.navigation_frame, text="<<", font=("Arial", 14), command=self.prev_month
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.month_label = tk.Label(
            self.navigation_frame, text="", font=("Arial", 18, "bold"), bg="#f0f0f0"
        )
        self.month_label.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            self.navigation_frame, text=">>", font=("Arial", 14), command=self.next_month
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH)

    def render_calendar(self):
        """Render the calendar grid based on the current month and tasks."""
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(text=self.current_date.strftime("%B %Y"))

        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=5, pady=5)

        first_day = self.current_date.replace(day=1)
        start_day = (first_day.weekday() + 1) % 7
        days_in_month = (first_day.replace(month=self.current_date.month % 12 + 1, day=1) - timedelta(days=1)).day

        row, col = 1, start_day
        for day in range(1, days_in_month + 1):
            date_str = self.current_date.replace(day=day).strftime("%Y-%m-%d")
            button_color = "#90CAF9" if date_str in tasks else "#E3F2FD"
            button = tk.Button(
                self.calendar_frame,
                text=str(day),
                width=10,
                height=3,
                bg=button_color,
                command=lambda d=day: self.show_tasks(d),
            )
            button.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def show_tasks(self, day):
        """Display the tasks for the selected day and allow adding/removing tasks."""
        self.selected_date = self.current_date.replace(day=day)
        date_str = self.selected_date.strftime("%Y-%m-%d")
        task_list = tasks.get(date_str, [])

        task_str = "\n".join(f"- {task}" for task in task_list) if task_list else "No tasks scheduled."
        response = messagebox.askyesnocancel("Tasks", f"Tasks for {date_str}:\n\n{task_str}\n\nYes: Add Task | No: Remove Task | Cancel: Close")
        if response is True:
            new_task = simpledialog.askstring("New Task", "Enter the topic you learned:")
            if new_task:
                self.schedule_memory(new_task)
            save_tasks()
            self.render_calendar()
        elif response is False:
            self.remove_task()

    def schedule_memory(self, topic):
        """Schedule memory revision for the topic on future dates based on defined intervals."""
        initial_date = self.selected_date
        for interval in SCHEDULE_INTERVALS:
            revision_date = (initial_date + timedelta(days=interval)).strftime("%Y-%m-%d")
            if revision_date not in tasks:
                tasks[revision_date] = []
            if topic not in tasks[revision_date]:
                tasks[revision_date].append(topic)

    def remove_task(self):
        """Remove a task from all scheduled dates."""
        date_str = self.selected_date.strftime("%Y-%m-%d")
        if date_str not in tasks or not tasks[date_str]:
            messagebox.showinfo("Remove Task", "No tasks to remove on this date.")
            return

        task_to_remove = simpledialog.askstring("Remove Task", "Enter the task to remove:")
        if task_to_remove:
            for date in list(tasks.keys()):
                if task_to_remove in tasks[date]:
                    tasks[date].remove(task_to_remove)
                if not tasks[date]:
                    del tasks[date]

            save_tasks()
            self.render_calendar()
            messagebox.showinfo("Success", f"Task '{task_to_remove}' removed successfully!")

    def prev_month(self):
        """Navigate to the previous month."""
        self.current_date = (self.current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        self.render_calendar()

    def next_month(self):
        """Navigate to the next month."""
        next_month = self.current_date.month % 12 + 1
        year = self.current_date.year + (1 if next_month == 1 else 0)
        self.current_date = self.current_date.replace(year=year, month=next_month, day=1)
        self.render_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
