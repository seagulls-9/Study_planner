import customtkinter as ctk
from datetime import datetime
import json
import os
import re
import threading
import webbrowser
from html.parser import HTMLParser
from tkinter import TclError, messagebox
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"
SUBJECTS_FILE = "subjects.json"
PMT_BASE_URL = "https://www.physicsandmathstutor.com"

# The ID is the short internal key used to connect homework to a subject.
# The name is the friendly name displayed to the user.
PMT_SUBJECTS = {
    "Maths": "maths",
    "Further Maths": "further-maths",
    "Biology": "biology",
    "Chemistry": "chemistry",
    "Physics": "physics",
    "Economics": "economics",
    "Geography": "geography",
    "English Literature": "english-literature",
    "Psychology": "psychology",
    "Computer Science": "computer-science",
}

# Existing PMT paths for the sciences/maths and the A-level board paths used by
# the other revision sections. Computer Science has its own PMT URL format.
PMT_SUBJECT_PATHS = {
    "maths": "maths/a-level",
    "further-maths": "maths/a-level/further-maths",
    "biology": "biology/a-level",
    "chemistry": "chemistry/a-level",
    "physics": "physics/a-level",
    "economics": "economics-revision",
    "geography": "geography-revision",
    "english-literature": "english-literature-revision",
    "psychology": "psychology-revision",
}
PMT_BOARD_PATHS = {
    "AQA": "aqa", "Edexcel": "edexcel", "OCR": "ocr",
    "OCR A": "ocr-a", "OCR B": "ocr-b", "CIE": "cie",
    "WJEC": "wjec", "Eduqas": "eduqas",
}
PMT_BOARDS = tuple(PMT_BOARD_PATHS.keys())
PMT_SUBJECT_NAMES = tuple(PMT_SUBJECTS.keys())


def make_id(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def pmt_page_url(subject, exam_board):
    subject_id = make_id(subject)
    board = str(exam_board).strip()
    board_path = PMT_BOARD_PATHS.get(board)
    if subject_id == "computer-science":
        computer_paths = {"AQA": "a-level-aqa", "OCR": "a-level-ocr"}
        path = computer_paths.get(board)
        return f"{PMT_BASE_URL}/computer-science-revision/{path}/" if path else None
    subject_path = PMT_SUBJECT_PATHS.get(subject_id)
    if not subject_path or not board_path:
        return None
    if subject_id in {"maths", "biology", "chemistry", "physics", "further-maths"}:
        return f"{PMT_BASE_URL}/{subject_path}/{board_path}/"
    return f"{PMT_BASE_URL}/{subject_path}/a-level-{board_path}/"


class PMTTopicParser(HTMLParser):
    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.links = []
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "a" or not self.current_href:
            return
        name = " ".join("".join(self.current_text).split())
        full_url = urljoin(self.page_url, self.current_href)
        page = urlparse(self.page_url)
        link = urlparse(full_url)
        ignored = {"", "home", "revision", "past papers", "mark schemes", "notes"}
        if (link.netloc == page.netloc and link.path.rstrip("/").startswith(page.path.rstrip("/"))
                and name and name.casefold() not in ignored
                and not link.path.lower().endswith((".pdf", ".doc", ".docx"))
                and not any(item["url"] == full_url for item in self.links)):
            self.links.append({"name": name, "notes": "", "url": full_url})
        self.current_href = None
        self.current_text = []


def fetch_pmt_topics(subject, exam_board):
    page_url = pmt_page_url(subject, exam_board)
    if not page_url:
        raise ValueError("Choose a supported PMT subject and exam board.")
    request = Request(page_url, headers={"User-Agent": "StudyPlanner/1.0"})
    with urlopen(request, timeout=15) as response:
        parser = PMTTopicParser(page_url)
        parser.feed(response.read().decode("utf-8", errors="ignore"))
    if not parser.links:
        raise ValueError("No topic links were found on the PMT page.")
    return parser.links, page_url


def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError as error:
        messagebox.showerror("Error", f"Failed to save data: {error}")


def load_subjects():
    data = load_json(SUBJECTS_FILE, [])
    if not isinstance(data, list):
        return []
    for subject in data:
        if isinstance(subject, dict):
            subject.setdefault("topics", [])
            subject.setdefault("notes", "")
            subject.setdefault("links", [])
            subject.setdefault("exam_board", "")
            subject.setdefault("pmt_url", "")
    return [subject for subject in data if isinstance(subject, dict)]


def normalise_tasks(data):
    result = []
    for task in data if isinstance(data, list) else []:
        if isinstance(task, dict):
            task.setdefault("subject_id", "")
            result.append(task)
        elif isinstance(task, str):
            parts = task.split(" - ", 1)
            result.append({"due_date": parts[0], "title": parts[-1],
                           "subject_id": "", "created_at": datetime.now().isoformat()})
    return result


def subject_name(subject_id):
    for subject in subjects:
        if subject.get("id") == subject_id:
            return subject.get("name", subject_id)
    return "No subject"


def format_task_display(task):
    date = task.get("due_date", "N/A")
    title = task.get("title", "N/A")
    subject_id = task.get("subject_id", "")
    prefix = f"[{subject_name(subject_id)}] " if subject_id else ""
    try:
        days = (datetime.strptime(date, "%Y-%m-%d") - datetime.today()).days
        status = "(Due TODAY)" if days == 0 else (
            f"(OVERDUE by {abs(days)} days)" if days < 0 else f"({days} days left)")
        return f"{date} - {prefix}{title} {status}"
    except ValueError:
        return f"{date} - {prefix}{title}"


subjects = load_subjects()
tasks = normalise_tasks(load_json(TASKS_FILE, []))

window = ctk.CTk()
window.title("Study Planner")
window.geometry("900x700")
window.minsize(750, 550)
ctk.CTkLabel(window, text="Study Planner", font=("Arial", 24, "bold")).pack(pady=10)
tabs = ctk.CTkTabview(window)
tabs.pack(fill="both", expand=True, padx=20, pady=(0, 15))
home_tab = tabs.add("Homework")
subjects_tab = tabs.add("Subjects & Topics")

input_frame = ctk.CTkFrame(home_tab)
input_frame.pack(fill="x", pady=10, padx=10)
ctk.CTkLabel(input_frame, text="Due Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
due_date_entry = ctk.CTkEntry(input_frame, width=180)
due_date_entry.grid(row=0, column=1, padx=5, pady=5)
ctk.CTkLabel(input_frame, text="Subject ID").grid(row=0, column=2, sticky="w", padx=5, pady=5)
subject_id_entry = ctk.CTkEntry(input_frame, width=180, placeholder_text="e.g. computer-science")
subject_id_entry.grid(row=0, column=3, padx=5, pady=5)
ctk.CTkLabel(input_frame, text="Homework").grid(row=1, column=0, sticky="w", padx=5, pady=5)
task_entry = ctk.CTkEntry(input_frame, width=570, placeholder_text="Homework title")
task_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

subject_form = ctk.CTkFrame(subjects_tab)
subject_form.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(subject_form, text="Subject ID (short key)").grid(row=0, column=0, padx=5, pady=5)
new_subject_id = ctk.CTkEntry(subject_form, width=160, placeholder_text="e.g. computer-science")
new_subject_id.grid(row=0, column=1, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Subject name (display name)").grid(row=0, column=2, padx=5, pady=5)
new_subject_name = ctk.CTkOptionMenu(subject_form, values=list(PMT_SUBJECT_NAMES), width=180)
new_subject_name.set(PMT_SUBJECT_NAMES[0])
new_subject_name.grid(row=0, column=3, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="ID: link used by homework; name: readable label").grid(
    row=0, column=5, columnspan=2, sticky="w", padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Exam board").grid(row=1, column=0, padx=5, pady=5)
exam_board_choice = ctk.CTkOptionMenu(subject_form, values=list(PMT_BOARDS), width=160)
exam_board_choice.set(PMT_BOARDS[0])
exam_board_choice.grid(row=1, column=1, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Notes").grid(row=1, column=2, padx=5, pady=5)
new_subject_notes = ctk.CTkEntry(subject_form, width=180, placeholder_text="Subject notes")
new_subject_notes.grid(row=1, column=3, padx=5, pady=5)
ctk.CTkLabel(subject_form, text="Links (one per line)").grid(row=2, column=0, padx=5, pady=5)
new_subject_links = ctk.CTkTextbox(subject_form, width=340, height=55)
new_subject_links.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
subject_sections = ctk.CTkScrollableFrame(subjects_tab, label_text="Your subjects")
subject_sections.pack(fill="both", expand=True, padx=10, pady=10)


def update_subject_id(selected_name):
    new_subject_id.delete(0, "end")
    new_subject_id.insert(0, PMT_SUBJECTS.get(selected_name, make_id(selected_name)))


new_subject_name.configure(command=update_subject_id)
update_subject_id(new_subject_name.get())


def refresh_task_list():
    task_list.configure(state="normal")
    task_list.delete("1.0", "end")
    for number, task in enumerate(tasks, 1):
        task_list.insert("end", f"{number}. {format_task_display(task)}\n")
    task_list.configure(state="disabled")


def add_task_gui():
    title, due, sid = task_entry.get().strip(), due_date_entry.get().strip(), subject_id_entry.get().strip()
    if not title or not due:
        messagebox.showerror("Error", "Please enter homework and a due date.")
        return
    try:
        datetime.strptime(due, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return
    if sid and not any(s.get("id") == sid for s in subjects):
        messagebox.showerror("Error", "That subject ID does not exist. Add the subject first.")
        return
    tasks.append({"due_date": due, "title": title, "subject_id": sid,
                  "created_at": datetime.now().isoformat()})
    tasks.sort(key=lambda item: item.get("due_date", "9999-99-99"))
    save_json(TASKS_FILE, tasks)
    task_entry.delete(0, "end")
    due_date_entry.delete(0, "end")
    refresh_task_list()


def complete_task_gui():
    try:
        selected = task_list.get("sel.first", "sel.last")
        number = int(selected.split(".", 1)[0]) - 1
        if not 0 <= number < len(tasks):
            raise ValueError
        tasks.pop(number)
        save_json(TASKS_FILE, tasks)
        refresh_task_list()
    except (ValueError, TclError):
        messagebox.showwarning("Warning", "Please select a homework item to complete.")


def clear_all_tasks():
    if messagebox.askyesno("Confirm", "Clear all homework?"):
        tasks.clear()
        save_json(TASKS_FILE, tasks)
        refresh_task_list()


def add_subject_gui():
    sid, name = make_id(new_subject_id.get().strip()), new_subject_name.get().strip()
    board = str(exam_board_choice.get()).strip()
    if not sid or not name:
        messagebox.showerror("Error", "Please choose a subject name and enter its subject ID.")
        return
    if any(s.get("id") == sid for s in subjects):
        messagebox.showerror("Error", "That subject ID already exists.")
        return
    if not pmt_page_url(name, board):
        messagebox.showerror("Error", "Choose a subject and a supported exam board.")
        return
    status_label.configure(text="Fetching PMT topics...")
    add_subject_button.configure(state="disabled")
    threading.Thread(target=finish_subject_add, args=(sid, name, board), daemon=True).start()


def finish_subject_add(sid, name, board):
    try:
        topics, url = fetch_pmt_topics(name, board)
        error = None
    except Exception as caught:
        topics, url, error = [], pmt_page_url(name, board), caught
    window.after(0, complete_subject_add, sid, name, board, topics, url, error)


def complete_subject_add(sid, name, board, topics, url, error):
    add_subject_button.configure(state="normal")
    if error:
        status_label.configure(text="Could not fetch PMT topics")
        if not messagebox.askyesno("PMT unavailable", f"{error}\n\nAdd the subject without topics?"):
            return
    links = [x.strip() for x in new_subject_links.get("1.0", "end").splitlines() if x.strip()]
    subjects.append({"id": sid, "name": name, "exam_board": board,
                     "notes": new_subject_notes.get().strip(), "links": links,
                     "topics": topics, "pmt_url": url})
    save_json(SUBJECTS_FILE, subjects)
    for entry in (new_subject_id, new_subject_notes):
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
        ctk.CTkLabel(section, text=f"{subject.get('name', 'Subject')}  ({subject.get('exam_board') or 'No board'})",
                     font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(section, text=f"Subject ID: {subject.get('id', '')}",
                     text_color="#aaaaaa").pack(anchor="w", padx=10)
        ctk.CTkLabel(section, text=f"Notes: {subject.get('notes') or 'None'}",
                     wraplength=760, justify="left").pack(anchor="w", padx=10)
        topics = subject.get("topics", [])
        names = "; ".join(topic.get("name", "Unnamed topic") for topic in topics if isinstance(topic, dict))
        ctk.CTkLabel(section, text=f"Topics: {names or 'None'}", wraplength=760,
                     justify="left").pack(anchor="w", padx=10, pady=(2, 2))
        url = subject.get("pmt_url")
        if url:
            link = ctk.CTkLabel(section, text="Open PMT page", text_color="#55aaff")
            link.pack(anchor="w", padx=10, pady=(0, 8))
            link.bind("<Button-1>", lambda _, page=url: webbrowser.open(page))


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
window.mainloop()
