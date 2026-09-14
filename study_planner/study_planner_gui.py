import customtkinter as ctk
from datetime import datetime
import os
from tkinter import messagebox

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def save_tasks(tasks):
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")

def load_tasks():
    tasks = []
    if os.path.exists("tasks.txt"):
        with open("tasks.txt", "r") as file:
            for line in file:
                tasks.append(line.strip())
    return tasks

def format_task_display(task):
    """Format task with days remaining or overdue status"""
    try:
        date_part = task.split(" - ")[0]
        due_date = datetime.strptime(date_part, "%Y-%m-%d")
        today = datetime.today()
        days_diff = (due_date - today).days
        
        if days_diff < 0:
            status = f"(OVERDUE by {abs(days_diff)} days)"
        elif days_diff == 0:
            status = "(Due TODAY)"
        else:
            status = f"({days_diff} days left)"
        
        return f"{task} {status}"
    except Exception as e:
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
    
    tasks.append(f"{due_date} - {task}")
    tasks.sort()
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
