import customtkinter as ctk
from datetime import datetime
import json
import os
import re
import webbrowser
from tkinter import messagebox

# Dark Mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"
SUBJECTS_FILE = "subjects.json"


def load_json(filename, default):
    """Load JSON data, returning default data when the file is missing or invalid."""
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError as error:
        messagebox.showerror("Error", f"Failed to save data: {error}")


def save_tasks(tasks):
    save_json(TASKS_FILE, tasks)


def load_tasks():
    return load_json(TASKS_FILE, [])


def save_subjects(subjects):
    save_json(SUBJECTS_FILE, subjects)


def load_subjects():
    subjects = load_json(SUBJECTS_FILE, [])
    if not isinstance(subjects, list):
        return []

    # Keep older subject files usable if they do not have topics yet.
    for subject in subjects:
        subject.setdefault("topics", [])
        subject.setdefault("notes", "")
        subject.setdefault("links", [])
    return subjects


def normalise_tasks(tasks):
    """Allow tasks created by the original version to continue working."""
    normalised = []
    for task in tasks:
        if isinstance(task, dict):
            task.setdefault("subject_id", "")
            normalised.append(task)
        elif isinstance(task, str):
            parts = task.split(" - ", 1)
            normalised.append({
                "due_date": parts[0],
                "title": parts[1] if len(parts) > 1 else task,
                "subject_id": "",
                "created_at": datetime.now().isoformat(),
            })
    return normalised


def subject_name(subject_id):
    for subject in subjects:
        if subject["id"] == subject_id:
            return subject["name"]
    return "No subject"


def format_task_display(task):
    date_part = task.get("due_date", "N/A")
    task_text = task.get("title", "N/A")
    subject_id = task.get("subject_id", "")
    subject_text = f"[{subject_name(subject_id)}] " if subject_id else ""

    try:
        days_diff = (datetime.strptime(date_part, "%Y-%m-%d") - datetime.today()).days
        if days_diff < 0:
            status = f"(OVERDUE by {abs(days_diff)} days)"
        elif days_diff == 0:
            status = "(Due TODAY)"
        else:
            status = f"({days_diff} days left)"
        return f"{date_part} - {subject_text}{task_text} {status}"
    except ValueError:
        return f"{date_part} - {subject_text}{task_text}"


def make_id(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


subjects = load_subjects()
tasks = normalise_tasks(load_tasks())

# Create main window
window = ctk.CTk()
window.title("Study Planner")
window.geometry("900x700")
window.minsize(750, 550)

ctk.CTkLabel(window, text="Study Planner", font=("Arial", 24, "bold")).pack(pady=10)
tabs = ctk.CTkTabview(window)
tabs.pack(fill="both", expand=True, padx=20, pady=(0, 15))
home_tab = tabs.add("Homework")
subjects_tab = tabs.add("Subjects & Topics")

# ---------------- Homework tab ----------------
input_frame = ctk.CTkFrame(home_tab)
input_frame.pack(fill="x", pady=10, padx=10)

ctk.CTkLabel(input_frame, text="Due Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
due_date_entry = ctk.CTkEntry(input_frame, width=180)
due_date_entry.grid(row=0, column=1, padx=5, pady=5)
ctk.CTkLabel(input_frame, text="Subject ID").grid(row=0, column=2, sticky="w", padx=5, pady=5)
subject_id_entry = ctk.CTkEntry(input_frame, width=180, placeholder_text="e.g. maths")
subject_id_entry.grid(row=0, column=3, padx=5, pady=5)
ctk.CTkLabel(input_frame, text="Homework").grid(row=1, column=0, sticky="w", padx=5, pady=5)
task_entry = ctk.CTkEntry(input_frame, width=570, placeholder_text="Homework title")
task_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

# ---------------- Subjects tab ----------------
subject_form = ctk.CTkFrame(subjects_tab)
subject_form.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(subject_form, text="Subject ID").grid(row=0, column=0, padx=5, pady=5)
new_subject_id = ctk.CTkEntry(subject_form, width=160, placeholder_text="e.g. maths")
new_subject_id.grid(row=0, column=1, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Subject name").grid(row=0, column=2, padx=5, pady=5)
new_subject_name = ctk.CTkEntry(subject_form, width=180)
new_subject_name.grid(row=0, column=3, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Notes").grid(row=1, column=0, padx=5, pady=5)
new_subject_notes = ctk.CTkEntry(subject_form, width=340, placeholder_text="Subject notes")
new_subject_notes.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Links (one per line)").grid(row=2, column=0, padx=5, pady=5)
new_subject_links = ctk.CTkTextbox(subject_form, width=340, height=55)
new_subject_links.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

subject_sections = ctk.CTkScrollableFrame(subjects_tab, label_text="Your subjects")
subject_sections.pack(fill="both", expand=True, padx=10, pady=10)


def refresh_task_list():
    task_list.configure(state="normal")
    task_list.delete("1.0", "end")
    for number, task in enumerate(tasks, 1):
        task_list.insert("end", f"{number}. {format_task_display(task)}\n")
    task_list.configure(state="disabled")


def refresh_subject_choices():
    values = [subject["id"] for subject in subjects] or ["No subjects yet"]
    subject_id_entry.configure(values=values) if hasattr(subject_id_entry, "configure") else None


def add_task_gui():
    task = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    subject_id = subject_id_entry.get().strip()
    if not task or not due_date:
        messagebox.showerror("Error", "Please enter homework and a due date.")
        return
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return
    if subject_id and not any(subject["id"] == subject_id for subject in subjects):
        messagebox.showerror("Error", "That subject ID does not exist. Add the subject first.")
        return

    tasks.append({"due_date": due_date, "title": task, "subject_id": subject_id,
                  "created_at": datetime.now().isoformat()})
    tasks.sort(key=lambda item: item.get("due_date", "9999-99-99"))
    save_tasks(tasks)
    task_entry.delete(0, "end")
    due_date_entry.delete(0, "end")
    refresh_task_list()


def complete_task_gui():
    try:
        selected = task_list.get("sel.first", "sel.last")
        task_num = int(selected.split(".", 1)[0]) - 1
        if 0 <= task_num < len(tasks):
            tasks.pop(task_num)
            save_tasks(tasks)
            refresh_task_list()
        else:
            raise ValueError
    except (ValueError, ctk.TclError):
        messagebox.showwarning("Warning", "Please select a homework item to complete.")


def clear_all_tasks():
    if messagebox.askyesno("Confirm", "Clear all homework?"):
        tasks.clear()
        save_tasks(tasks)
        refresh_task_list()


def add_subject_gui():
    subject_id = make_id(new_subject_id.get().strip())
    name = new_subject_name.get().strip()
    if not subject_id or not name:
        messagebox.showerror("Error", "Please enter both a subject ID and name.")
        return
    if any(subject["id"] == subject_id for subject in subjects):
        messagebox.showerror("Error", "That subject ID already exists.")
        return
    links = [link.strip() for link in new_subject_links.get("1.0", "end").splitlines() if link.strip()]
    subjects.append({"id": subject_id, "name": name, "notes": new_subject_notes.get().strip(),
                     "links": links, "topics": []})
    save_subjects(subjects)
    for entry in (new_subject_id, new_subject_name, new_subject_notes):
        entry.delete(0, "end")
    new_subject_links.delete("1.0", "end")
    refresh_subject_sections()
    messagebox.showinfo("Success", f"Subject '{name}' added.")


def refresh_subject_sections():
    for child in subject_sections.winfo_children():
        child.destroy()
    if not subjects:
        ctk.CTkLabel(subject_sections, text="Add a subject above to create its section.").pack(pady=20)
        return
    for subject in subjects:
        section = ctk.CTkFrame(subject_sections)
        section.pack(fill="x", padx=5, pady=6)
        ctk.CTkLabel(section, text=f"{subject['name']}  (ID: {subject['id']})",
                     font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(section, text=f"Notes: {subject.get('notes') or 'None'}",
                     wraplength=760, justify="left").pack(anchor="w", padx=10)
        links = subject.get("links", [])
        ctk.CTkLabel(section, text="Links: " + (" | ".join(links) if links else "None"),
                     wraplength=760, justify="left").pack(anchor="w", padx=10)
        topics = subject.get("topics", [])
        topic_text = "Topics: " + ("; ".join(f"{topic['name']} ({topic.get('notes') or 'no notes'})" for topic in topics)
                                     if topics else "None")
        ctk.CTkLabel(section, text=topic_text, wraplength=760, justify="left").pack(anchor="w", padx=10, pady=(2, 8))


# Buttons and lists
ctk.CTkButton(subject_form, text="Add Subject", command=add_subject_gui, width=140).grid(row=0, column=4, rowspan=3, padx=10)
ctk.CTkButton(subjects_tab, text="Refresh subject sections", command=refresh_subject_sections).pack(pady=(0, 8))

task_list = ctk.CTkTextbox(home_tab, height=300, font=("Arial", 11))
task_list.pack(fill="both", expand=True, padx=10, pady=10)
task_list.configure(state="disabled")
button_frame = ctk.CTkFrame(home_tab)
button_frame.pack(pady=10)
ctk.CTkButton(button_frame, text="Add Homework", command=add_task_gui, width=150).grid(row=0, column=0, padx=5)
ctk.CTkButton(button_frame, text="Complete Homework", command=complete_task_gui, width=150).grid(row=0, column=1, padx=5)
ctk.CTkButton(button_frame, text="Clear All", command=clear_all_tasks, width=150, fg_color="red").grid(row=0, column=2, padx=5)

refresh_task_list()
refresh_subject_sections()
refresh_subject_choices()
window.mainloop()
