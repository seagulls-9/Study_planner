tasks = []
def add_task(tasks)
    task = input("Enter a task: ")
        tasks.append(task)
def view_tasks(tasks):
    for task in tasks:
    print(task)
    
while True:
    print("--- Study Planner ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_task(tasks)

    elif choice == "2":
        view_tasks(tasks)

    elif choice == "3":
        print("Goodbye")
        break

    else:
        print("Invalid option")