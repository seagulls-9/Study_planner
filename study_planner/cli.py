"""Terminal interface. Run with: python -m study_planner.cli"""
from .pmt_service import PMT_SUBJECTS, PMT_BOARDS
from .service import PlannerService


def print_tasks(service: PlannerService) -> None:
    if not service.tasks: print("No tasks available."); return
    names = {s.id: s.name for s in service.subjects}
    for number, task in enumerate(service.tasks, 1): print(f"{number}. {task.due_date} - [{names.get(task.subject_id, 'No subject')}] {task.title} ({task.display_status()})")


def run() -> None:
    service = PlannerService()
    while True:
        print("\n--- Study Planner (CLI) ---\n1. Add task\n2. View tasks\n3. Complete task\n4. Clear tasks\n5. Add subject\n6. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1": service.add_task(input("Task: "), input("Due date (YYYY-MM-DD): "), input("Subject ID (optional): ")); print("Task added.")
            elif choice == "2": print_tasks(service)
            elif choice == "3": service.complete_task(int(input("Task number: ")) - 1); print("Task completed.")
            elif choice == "4": service.clear_tasks(); print("Tasks cleared.")
            elif choice == "5":
                print("Subjects:", ", ".join(PMT_SUBJECTS)); service.add_subject(input("ID: "), input("Name: "), input(f"Exam board ({', '.join(PMT_BOARDS)}): ")); print("Subject added.")
            elif choice == "6": print("Goodbye!"); return
            else: print("Invalid option.")
        except (ValueError, IndexError) as error: print(f"Error: {error}")


if __name__ == "__main__": run()
