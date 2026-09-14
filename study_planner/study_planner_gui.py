import tkinter as tk
from datetime import datetime
import os

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
    except:
        return task

window = tk.Tk()
window.title("Study Planner")
window.geometry("600x500")
window.config(bg="#f0f0f0")

# Input Frame
input_frame = tk.Frame(window, bg="#f0f0f0")
input_frame.pack(pady=10)

due_label = tk.Label(input_frame, text="Due Date (YYYY-MM-DD)", bg="#f0f0f0", font=("Arial", 10))
due_label.grid(row=0, column=0, sticky="w", padx=5)

due_date_entry = tk.Entry(input_frame, width=25)
due_date_entry.grid(row=0, column=1, padx=5)

task_label = tk.Label(input_frame, text="Task", bg="#f0f0f0", font=("Arial", 10))
task_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

task_entry = tk.Entry(input_frame, width=25)
task_entry.grid(row=1, column=1, padx=5, pady=5)

# Task List
task_list = tk.Listbox(window, font=("Arial", 10), height=15)
task_list.pack(fill="both", expand=True, padx=10, pady=10)

tasks = load_tasks()

def refresh_list():
    task_list.delete(0, tk.END)
    for task in tasks:
        task_list.insert(tk.END, format_task_display(task))

refresh_list()

def complete_task_gui():
    selected = task_list.curselection()
    if selected:
        tasks.pop(selected[0])
        save_tasks(tasks)
        refresh_list()
    else:
        tk.messagebox.showwarning("Warning", "Please select a task to complete.")

def add_task_gui():
    task = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    
    if not task or not due_date:
        tk.messagebox.showerror("Error", "Please enter both task and due date.")
        return
    
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        tk.messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return
    
    tasks.append(f"{due_date} - {task}")
    tasks.sort()
    save_tasks(tasks)
    
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    refresh_list()

def clear_all_tasks():
    if tk.messagebox.askyesno("Confirm", "Clear all tasks?"):
        tasks.clear()
        save_tasks(tasks)
        refresh_list()

# Button Frame
button_frame = tk.Frame(window, bg="#f0f0f0")
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Task", command=add_task_gui, bg="#4CAF50", fg="white", width=15)
add_button.grid(row=0, column=0, padx=5)

complete_button = tk.Button(button_frame, text="Complete Task", command=complete_task_gui, bg="#2196F3", fg="white", width=15)
complete_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(button_frame, text="Clear All", command=clear_all_tasks, bg="#f44336", fg="white", width=15)
clear_button.grid(row=0, column=2, padx=5)

window.mainloop()
