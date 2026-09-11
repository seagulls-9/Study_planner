tasks = []
def add_task(tasks)
    task = input("Enter a task: ")
        tasks.append(task)
def view_tasks(tasks):
    for i in range(len(tasks)):
        print(f"{i +1}. {tasks[i]}")
def complete_tasks(tasks):
    comptask = int(input("What is the number of the completed task? ")) - 1

    if 0 <= comptask < len(tasks):
        tasks.pop(comptask)
        print("Task removed. Well done!")
    else:
        print("Invalid task number.")
while True:
    print("--- Study Planner ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Complete tasks")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_task(tasks)

    elif choice == "2":
        view_tasks(tasks)
    
    elif choice == "3"
        complete_tasks(tasks)

    elif choice == "4":
        print("Goodbye")
        break

    else:
        print("Invalid option")
