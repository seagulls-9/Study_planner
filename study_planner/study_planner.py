def clear_tasks(tasks):
    tasks.clear()
    save_tasks(tasks)
    print("All tasks removed.")
def load_tasks():
    tasks = []

    file = open("tasks.txt", "r")

    for line in file:
        tasks.append(line.strip())

    file.close()

    return tasks
tasks = load_tasks()
def add_task(tasks):
    task = input("Enter task: ")
    due_date = input("Due date (YYYY-MM-DD): ")
    tasks.append(f"{due_date} - {task}")
    tasks.sort()
    save_tasks(tasks)
def view_tasks(tasks):
    if len(tasks) == 0:
        print("No tasks available.")
    else:
        for i in range(len(tasks)):
            print(f"{i + 1}. {tasks[i]}")
def complete_tasks(tasks):
    comptask = int(input("What is the number of the completed task? ")) - 1

    if 0 <= comptask < len(tasks):
        tasks.pop(comptask)
        save_tasks(tasks)
        print("Task removed. Well done!")
    else:
        print("Invalid task number.")
def save_tasks(tasks):
    file = open("tasks.txt", "w")

    for task in tasks:
        file.write(task + "\n")

    file.close()
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
