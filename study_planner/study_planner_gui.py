import customtkinter as ctk
from datetime import datetime
import json
import os
import re
import threading
import webbrowser
from html.parser import HTMLParser
from tkinter import messagebox
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# Dark Mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"
SUBJECTS_FILE = "subjects.json"
PMT_BASE_URL = "https://www.physicsandmathstutor.com"
PMT_SUBJECT_PATHS = {
    "maths": "maths/a-level",
    "mathematics": "maths/a-level",
    "biology": "biology/a-level",
    "chemistry": "chemistry/a-level",
    "physics": "physics/a-level",
}
PMT_BOARD_PATHS = {
    "AQA": "aqa",
    "Edexcel": "edexcel",
    "OCR": "ocr",
    "OCR A": "ocr-a",
    "OCR B": "ocr-b",
    "CIE": "cie",
    "WJEC": "wjec",
    "Eduqas": "eduqas",
}


class PMTTopicParser(HTMLParser):
    """Extract likely topic links from a PMT subject/exam-board page."""

    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.links = []
        self._current_link = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href", "")
            self._current_link = href
            self._text = []

    def handle_data(self, data):
        if self._current_link is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "a" or self._current_link is None:
            return
        text = " ".join("".join(self._text).split())
        full_url = urljoin(self.page_url, self._current_link)
        parsed = urlparse(full_url)
        page_path = urlparse(self.page_url).path.rstrip("/")
        link_path = parsed.path.rstrip("/")
        ignored = {"", "home", "revision", "past papers", "mark schemes", "notes"}
        if (parsed.netloc == urlparse(self.page_url).netloc
                and link_path.startswith(page_path)
                and text
                and text.casefold() not in ignored
                and not link_path.lower().endswith((".pdf", ".doc", ".docx"))
                and full_url not in {item["url"] for item in self.links}):
            self.links.append({"name": text, "notes": "", "url": full_url})
        self._current_link = None
        self._text = []


def pmt_page_url(subject, exam_board):
    subject_path = PMT_SUBJECT_PATHS.get(make_id(subject).replace("-", ""))
    board_path = PMT_BOARD_PATHS.get(exam_board)
    if not subject_path or not board_path:
        return None
    return f"{PMT_BASE_URL}/{subject_path}/{board_path}/"


def fetch_pmt_topics(subject, exam_board):
    page_url = pmt_page_url(subject, exam_board)
    if not page_url:
        raise ValueError("PMT currently supports Maths, Biology, Chemistry and Physics for these boards.")
    request = Request(page_url, headers={"User-Agent": "StudyPlanner/1.0"})
    with urlopen(request, timeout=15) as response:
        parser = PMTTopicParser(page_url)
        parser.feed(response.read().decode("utf-8", errors="ignore"))
    if not parser.links:
        raise ValueError("No topic links were found on the PMT page.")
    return parser.links, page_url


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
        subject.setdefault("exam_board", "")
        subject.setdefault("pmt_url", "")
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
ctk.CTkLabel(subject_form, text="Exam board").grid(row=1, column=0, padx=5, pady=5)
exam_board_choice = ctk.CTkComboBox(subject_form, values=list(PMT_BOARD_PATHS), width=160)
exam_board_choice.set("AQA")
exam_board_choice.grid(row=1, column=1, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Notes").grid(row=1, column=2, padx=5, pady=5)
new_subject_notes = ctk.CTkEntry(subject_form, width=180, placeholder_text="Subject notes")
new_subject_notes.grid(row=1, column=3, padx=5, pady=5)
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
    # Kept for compatibility with the existing text-entry homework form.
    return None


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
    exam_board = exam_board_choice.get().strip()
    if not subject_id or not name:
        messagebox.showerror("Error", "Please enter a subject ID and name.")
        return
    if any(subject["id"] == subject_id for subject in subjects):
        messagebox.showerror("Error", "That subject ID already exists.")
        return
    if not pmt_page_url(name, exam_board):
        messagebox.showerror("Error", "Use Maths, Biology, Chemistry or Physics as the subject name.")
        return

    status_label.configure(text="Fetching PMT topics...")
    add_subject_button.configure(state="disabled")
    threading.Thread(target=finish_subject_add, args=(subject_id, name, exam_board), daemon=True).start()


def finish_subject_add(subject_id, name, exam_board):
    try:
        topics, pmt_url = fetch_pmt_topics(name, exam_board)
        error = None
    except Exception as caught_error:
        topics, pmt_url, error = [], pmt_page_url(name, exam_board), caught_error
    window.after(0, complete_subject_add, subject_id, name, exam_board, topics, pmt_url, error)


def complete_subject_add(subject_id, name, exam_board, topics, pmt_url, error):
    add_subject_button.configure(state="normal")
    if error:
        status_label.configure(text="Could not fetch PMT topics")
        if not messagebox.askyesno("PMT unavailable", f"{error}\n\nAdd the subject without topics?"):
            return
    links = [link.strip() for link in new_subject_links.get("1.0", "end").splitlines() if link.strip()]
    subjects.append({"id": subject_id, "name": name, "exam_board": exam_board,
                     "notes": new_subject_notes.get().strip(), "links": links,
                     "topics": topics, "pmt_url": pmt_url})
    save_subjects(subjects)
    for entry in (new_subject_id, new_subject_name, new_subject_notes):
        entry.delete(0, "end")
    new_subject_links.delete("1.0", "end")
    status_label.configure(text=f"Added {len(topics)} PMT topics")
    refresh_subject_sections()
    messagebox.showinfo("Success", f"Subject '{name}' added with {len(topics)} PMT topics.")


def refresh_subject_sections():
    for child in subject_sections.winfo_children():
        child.destroy()
    if not subjects:
        ctk.CTkLabel(subject_sections, text="Add a subject above to create its section.").pack(pady=20)
        return
    for subject in subjects:
        section = ctk.CTkFrame(subject_sections)
        section.pack(fill="x", padx=5, pady=6)
        ctk.CTkLabel(section, text=f"{subject['name']}  ({subject.get('exam_board') or 'No board'})",
                     font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(section, text=f"Notes: {subject.get('notes') or 'None'}",
                     wraplength=760, justify="left").pack(anchor="w", padx=10)
        topics = subject.get("topics", [])
        topic_text = "Topics: " + ("; ".join(topic.get("name", "Unnamed topic") for topic in topics)
                                   if topics else "None")
        ctk.CTkLabel(section, text=topic_text, wraplength=760, justify="left").pack(anchor="w", padx=10, pady=(2, 2))
        if subject.get("pmt_url"):
            pmt_link = ctk.CTkLabel(section, text="Open PMT page", text_color="#55aaff", cursor="hand2")
            pmt_link.pack(anchor="w", padx=10, pady=(0, 8))
            pmt_link.bind("<Button-1>", lambda _, url=subject["pmt_url"]: webbrowser.open(url))


# Buttons and lists
add_subject_button = ctk.CTkButton(subject_form, text="Add Subject", command=add_subject_gui, width=140)
add_subject_button.grid(row=0, column=4, rowspan=3, padx=10)
status_label = ctk.CTkLabel(subjects_tab, text="")
status_label.pack(pady=(0, 2))
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
