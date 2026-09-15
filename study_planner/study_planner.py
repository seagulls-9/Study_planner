from datetime import datetime
import json
import os

TASKS_FILE = "tasks.json"

def clear_tasks(tasks):
    tasks.clear()
    save_tasks(tasks)
    print("All tasks removed.")

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

def add_task(tasks):
    task = input("Enter task: ")
    due_date = input("Due date (YYYY-MM-DD): ")
    
    # Validate date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return
    
    new_task = {
        "due_date": due_date,
        "title": task,
        "created_at": datetime.now().isoformat()
    }
    tasks.append(new_task)
    tasks.sort(key=lambda x: x["due_date"])
    save_tasks(tasks)
    print("Task added successfully!")

def view_tasks(tasks):
    if len(tasks) == 0:
        print("No tasks available.")
    else:
        today = datetime.today()
        for i in range(len(tasks)):
            task = tasks[i]
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_left = (due_date - today).days
            
            if days_left < 0:
                status = f"OVERDUE by {abs(days_left)} days"
            elif days_left == 0:
                status = "Due TODAY"
            else:
                status = f"{days_left} days left"
            
            print(f"{i + 1}. {task['due_date']} - {task['title']} ({status})")

def complete_tasks(tasks):
    comptask = int(input("What is the number of the completed task? ")) - 1

    if 0 <= comptask < len(tasks):
        tasks.pop(comptask)
        save_tasks(tasks)
        print("Task removed. Well done!")
    else:
        print("Invalid task number.")

def save_tasks(tasks):
    """Save tasks to JSON file"""
    try:
        with open(TASKS_FILE, "w") as file:
            json.dump(tasks, file, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {str(e)}")

tasks = load_tasks()

while True:
    print("--- Study Planner ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Complete Tasks")
    print("4. Clear Tasks")
    print("5. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_task(tasks)

    elif choice == "2":
        view_tasks(tasks)
    
    elif choice == "3":
        complete_tasks(tasks)
    
    elif choice == "4":
        clear_tasks(tasks)

    elif choice == "5":
        print("Goodbye")
        break

    else:
        print("Invalid option")
