import customtkinter as ctk
from datetime import datetime
import os
import json
from tkinter import messagebox

# Dark Mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"

def save_tasks(tasks):
    """Save tasks to JSON file"""
    try:
        with open(TASKS_FILE, "w") as file:
            json.dump(tasks, file, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")

def load_tasks():
    """Load tasks from JSON file"""
    tasks = []
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as file:
                tasks = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            tasks = []
    return tasks

def format_task_display(task):
    """Format task with days remaining or overdue status"""
    try:
        # Handle both old string format and new dict format
        if isinstance(task, dict):
            date_part = task.get("due_date", "")
            task_text = task.get("title", "")
        else:
            date_part = task.split(" - ")[0]
            task_text = " - ".join(task.split(" - ")[1:])
        
        due_date = datetime.strptime(date_part, "%Y-%m-%d")
        today = datetime.today()
        days_diff = (due_date - today).days
        
        if days_diff < 0:
            status = f"(OVERDUE by {abs(days_diff)} days)"
        elif days_diff == 0:
            status = "(Due TODAY)"
        else:
            status = f"({days_diff} days left)"
        
        return f"{date_part} - {task_text} {status}"
    except Exception as e:
        if isinstance(task, dict):
            return f"{task.get('due_date', 'N/A')} - {task.get('title', 'N/A')}"
        return task

# Create main window
window = ctk.CTk()
window.title("Study Planner")
window.geometry("700x600")

# Title
title_label = ctk.CTkLabel(window, text="Study Planner", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

# Input Frame
input_frame = ctk.CTkFrame(window)
input_frame.pack(pady=10, padx=20)

due_label = ctk.CTkLabel(input_frame, text="Due Date (YYYY-MM-DD)", font=("Arial", 12))
due_label.grid(row=0, column=0, sticky="w", padx=5)

due_date_entry = ctk.CTkEntry(input_frame, width=200)
due_date_entry.grid(row=0, column=1, padx=5)

task_label = ctk.CTkLabel(input_frame, text="Task", font=("Arial", 12))
task_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)

task_entry = ctk.CTkEntry(input_frame, width=200)
task_entry.grid(row=1, column=1, padx=5, pady=10)

# Task List
task_list = ctk.CTkTextbox(window, height=250, width=650, font=("Arial", 11))
task_list.pack(fill="both", expand=True, padx=20, pady=10)
task_list.configure(state="disabled")

tasks = load_tasks()

def refresh_list():
    task_list.configure(state="normal")
    task_list.delete("1.0", "end")
    for i, task in enumerate(tasks, 1):
        task_list.insert("end", f"{i}. {format_task_display(task)}\n")
    task_list.configure(state="disabled")

refresh_list()

def complete_task_gui():
    if not tasks:
        messagebox.showwarning("Warning", "No tasks available.")
        return
    
    try:
        selected_text = task_list.get("sel.first", "sel.last")
        # Extract task number from selected text
        task_num = int(selected_text.split(".")[0]) - 1
        
        if 0 <= task_num < len(tasks):
            tasks.pop(task_num)
            save_tasks(tasks)
            refresh_list()
        else:
            messagebox.showerror("Error", "Invalid task selection.")
    except:
        messagebox.showwarning("Warning", "Please select a task to complete.")

def add_task_gui():
    task = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    
    if not task or not due_date:
        messagebox.showerror("Error", "Please enter both task and due date.")
        return
    
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return
    
    # Create task as dictionary
    new_task = {
        "due_date": due_date,
        "title": task,
        "created_at": datetime.now().isoformat()
    }
    
    tasks.append(new_task)
    # Sort by due_date
    tasks.sort(key=lambda x: x["due_date"])
    save_tasks(tasks)
    
    task_entry.delete(0, "end")
    due_date_entry.delete(0, "end")
    refresh_list()
    messagebox.showinfo("Success", "Task added successfully!")

def clear_all_tasks():
    if messagebox.askyesno("Confirm", "Clear all tasks?"):
        tasks.clear()
        save_tasks(tasks)
        refresh_list()

# Button Frame
button_frame = ctk.CTkFrame(window)
button_frame.pack(pady=15)

add_button = ctk.CTkButton(button_frame, text="Add Task", command=add_task_gui, width=140)
add_button.grid(row=0, column=0, padx=5)

complete_button = ctk.CTkButton(button_frame, text="Complete Task", command=complete_task_gui, width=140)
complete_button.grid(row=0, column=1, padx=5)

clear_button = ctk.CTkButton(button_frame, text="Clear All", command=clear_all_tasks, width=140, fg_color="red")
clear_button.grid(row=0, column=2, padx=5)

window.mainloop()
