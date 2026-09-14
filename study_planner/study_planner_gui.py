import tkinter as tk

def save_tasks(tasks):
    file = open("tasks.txt", "w")

    for task in tasks:
        file.write(task + "\n")

    file.close()
    
def load_tasks():
    tasks = []

    file = open("tasks.txt", "r")

    for line in file:
        tasks.append(line.strip())

    file.close()

tasks = load_tasks()

for task in tasks:
    task_list.insert(tk.END, task)
    
def refresh_list():
    task_list.delete(0, tk.END)
    for task in tasks:
        task_list.insert(tk.end, task)
def complete_task_gui():
    selected = task_list.curselection()

    if selected:
        tasks.pop(selected[0])
        save_tasks(tasks)
        refresh_list()

def add_task_gui():
    task = task_entry.get()
    due_date = due_date_entry.get()

    tasks.append(f"{due_date} - {task}")
    tasks.sort()
    save_tasks(tasks)

    refresh_list()

window = tk.Tk()
window.title("study planner")
window.geometry("500x400")

due_label = tk.Label(window, text="Due Date (YYYY-MM-DD)")
due_label.pack()

due_entry = tk.Entry(window)
due_entry.pack()

task_entry = tk.Entry(window)
task_entry.pack()

add_button = tk.Button(window, text="Add Task")
add_button.pack()

complete_button = tk.Button(
    window,
    text="Complete Task",
    command=complete_task_gui
)

task_list = tk.Listbox(window)
task_list.pack(fill="both", expand=True)
              
window.mainloop()
