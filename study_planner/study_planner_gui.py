import customtkinter as ctk
from datetime import datetime
import json
from pathlib import Path
import re
import threading
import webbrowser
from html.parser import HTMLParser
from tkinter import TclError, messagebox
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_FILE = BASE_DIR / "tasks.json"
SUBJECTS_FILE = BASE_DIR / "subjects.json"
PMT_BASE_URL = "https://www.physicsandmathstutor.com"

PMT_SUBJECTS = {
    "Maths": "maths", "Further Maths": "further-maths", "Biology": "biology",
    "Chemistry": "chemistry", "Physics": "physics", "Economics": "economics",
    "Geography": "geography", "English Literature": "english-literature",
    "Psychology": "psychology", "Computer Science": "computer-science",
}
PMT_SUBJECT_PATHS = {
    "maths": "maths/a-level", "further-maths": "maths/a-level/further-maths",
    "biology": "biology/a-level", "chemistry": "chemistry/a-level",
    "physics": "physics/a-level", "economics": "economics-revision",
    "geography": "geography-revision", "english-literature": "english-literature-revision",
    "psychology": "psychology-revision",
}
PMT_BOARD_PATHS = {
    "AQA": "aqa", "Edexcel": "edexcel", "OCR": "ocr", "OCR A": "ocr-a",
    "OCR B": "ocr-b", "CIE": "cie", "WJEC": "wjec", "Eduqas": "eduqas",
}
PMT_BOARDS = tuple(PMT_BOARD_PATHS)
PMT_SUBJECT_NAMES = tuple(PMT_SUBJECTS)


def make_id(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def pmt_page_url(subject, exam_board):
    subject_id = make_id(subject)
    board = str(exam_board).strip()
    if subject_id == "computer-science":
        path = {"AQA": "a-level-aqa", "OCR": "a-level-ocr"}.get(board)
        return f"{PMT_BASE_URL}/computer-science-revision/{path}/" if path else None
    subject_path = PMT_SUBJECT_PATHS.get(subject_id)
    board_path = PMT_BOARD_PATHS.get(board)
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
        if tag.lower() == "a" and self.current_href is None:
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "a" or not self.current_href:
            return
        name = " ".join("".join(self.current_text).split())
        full_url, _ = urldefrag(urljoin(self.page_url, self.current_href))
        page, link = urlparse(self.page_url), urlparse(full_url)
        page_path, link_path = page.path.rstrip("/"), link.path.rstrip("/")
        ignored = {"", "home", "revision", "past papers", "mark schemes", "notes"}
        in_section = link_path == page_path or link_path.startswith(page_path + "/")
        if (link.netloc == page.netloc and in_section and name and name.casefold() not in ignored
                and not link_path.lower().endswith((".pdf", ".doc", ".docx"))
                and not any(item["url"] == full_url for item in self.links)):
            self.links.append({"name": name, "notes": "", "url": full_url})
        self.current_href, self.current_text = None, []


def fetch_pmt_topics(subject, exam_board):
    page_url = pmt_page_url(subject, exam_board)
    if not page_url:
        raise ValueError("Choose a supported PMT subject and exam board.")
    request = Request(page_url, headers={"User-Agent": "StudyPlanner/1.0"})
    with urlopen(request, timeout=15) as response:
        if getattr(response, "status", 200) >= 400:
            raise HTTPError(page_url, response.status, "PMT returned an error", response.headers, None)
        parser = PMTTopicParser(page_url)
        parser.feed(response.read().decode(response.headers.get_content_charset() or "utf-8", errors="ignore"))
    if not parser.links:
        raise ValueError("No topic links were found on the PMT page.")
    return parser.links, page_url


def load_json(filename, default):
    try:
        with Path(filename).open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    path = Path(filename)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
            file.write("\n")
        temporary.replace(path)
    except OSError as error:
        messagebox.showerror("Error", f"Failed to save data: {error}")


def load_subjects():
    data = load_json(SUBJECTS_FILE, [])
    if not isinstance(data, list):
        return []
    result = []
    for subject in data:
        if isinstance(subject, dict):
            subject.setdefault("topics", [])
            subject.setdefault("notes", "")
            subject.setdefault("links", [])
            subject.setdefault("exam_board", "")
            subject.setdefault("pmt_url", "")
            result.append(subject)
    return result


def normalise_tasks(data):
    result = []
    for task in data if isinstance(data, list) else []:
        if isinstance(task, dict):
            task.setdefault("subject_id", "")
            result.append(task)
        elif isinstance(task, str):
            parts = task.split(" - ", 1)
            result.append({"due_date": parts[0], "title": parts[-1], "subject_id": "",
                           "created_at": datetime.now().isoformat()})
    return result


def task_sort_key(task):
    try:
        return datetime.strptime(str(task.get("due_date", "")), "%Y-%m-%d")
    except (TypeError, ValueError):
        return datetime.max


class StudyPlannerApp:
    def __init__(self, window):
        self.window = window
        self.subjects = load_subjects()
        self.tasks = normalise_tasks(load_json(TASKS_FILE, []))
        self.window.title("Study Planner")
        self.window.geometry("900x700")
        self.window.minsize(750, 550)
        self.build_ui()
        self.refresh_task_list()
        self.refresh_subject_sections()

    def subject_name(self, subject_id):
        return next((s.get("name", subject_id) for s in self.subjects if s.get("id") == subject_id), "No subject")

    def format_task_display(self, task):
        date, title, sid = task.get("due_date", "N/A"), task.get("title", "N/A"), task.get("subject_id", "")
        prefix = f"[{self.subject_name(sid)}] " if sid else ""
        try:
            days = (datetime.strptime(date, "%Y-%m-%d").date() - datetime.now().date()).days
            status = "(Due TODAY)" if days == 0 else (f"(OVERDUE by {abs(days)} days)" if days < 0 else f"({days} days left)")
            return f"{date} - {prefix}{title} {status}"
        except (TypeError, ValueError):
            return f"{date} - {prefix}{title}"

    def build_ui(self):
        ctk.CTkLabel(self.window, text="Study Planner", font=("Arial", 24, "bold")).pack(pady=10)
        tabs = ctk.CTkTabview(self.window)
        tabs.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.home_tab, self.subjects_tab = tabs.add("Homework"), tabs.add("Subjects & Topics")
        self.build_home_tab()
        self.build_subjects_tab()

    def build_home_tab(self):
        frame = ctk.CTkFrame(self.home_tab); frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(frame, text="Due Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
        self.due_date_entry = ctk.CTkEntry(frame, width=180); self.due_date_entry.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame, text="Subject ID").grid(row=0, column=2, padx=5, pady=5)
        self.subject_id_entry = ctk.CTkEntry(frame, width=180, placeholder_text="e.g. computer-science"); self.subject_id_entry.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(frame, text="Homework").grid(row=1, column=0, padx=5, pady=5)
        self.task_entry = ctk.CTkEntry(frame, width=570, placeholder_text="Homework title"); self.task_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        self.task_list = ctk.CTkTextbox(self.home_tab, height=300, font=("Arial", 11)); self.task_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.task_list.configure(state="disabled")
        buttons = ctk.CTkFrame(self.home_tab); buttons.pack(pady=10)
        ctk.CTkButton(buttons, text="Add Homework", command=self.add_task_gui, width=150).grid(row=0, column=0, padx=5)
        ctk.CTkButton(buttons, text="Complete Homework", command=self.complete_task_gui, width=150).grid(row=0, column=1, padx=5)
        ctk.CTkButton(buttons, text="Clear All", command=self.clear_all_tasks, width=150, fg_color="red").grid(row=0, column=2, padx=5)

    def build_subjects_tab(self):
        form = ctk.CTkFrame(self.subjects_tab); form.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(form, text="Subject ID (short key)").grid(row=0, column=0, padx=5, pady=5)
        self.new_subject_id = ctk.CTkEntry(form, width=160, placeholder_text="e.g. computer-science"); self.new_subject_id.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(form, text="Subject name").grid(row=0, column=2, padx=5, pady=5)
        self.new_subject_name = ctk.CTkOptionMenu(form, values=list(PMT_SUBJECT_NAMES), width=180, command=self.update_subject_id); self.new_subject_name.set(PMT_SUBJECT_NAMES[0]); self.new_subject_name.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(form, text="Exam board").grid(row=1, column=0, padx=5, pady=5)
        self.exam_board_choice = ctk.CTkOptionMenu(form, values=list(PMT_BOARDS), width=160); self.exam_board_choice.set(PMT_BOARDS[0]); self.exam_board_choice.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(form, text="Notes").grid(row=1, column=2, padx=5, pady=5)
        self.new_subject_notes = ctk.CTkEntry(form, width=180, placeholder_text="Subject notes"); self.new_subject_notes.grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkLabel(form, text="Links (one per line)").grid(row=2, column=0, padx=5, pady=5)
        self.new_subject_links = ctk.CTkTextbox(form, width=340, height=55); self.new_subject_links.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        self.add_subject_button = ctk.CTkButton(form, text="Add Subject", command=self.add_subject_gui, width=140); self.add_subject_button.grid(row=0, column=4, rowspan=3, padx=10)
        self.subject_sections = ctk.CTkScrollableFrame(self.subjects_tab, label_text="Your subjects"); self.subject_sections.pack(fill="both", expand=True, padx=10, pady=10)
        self.status_label = ctk.CTkLabel(self.subjects_tab, text=""); self.status_label.pack(pady=(0, 2))
        ctk.CTkButton(self.subjects_tab, text="Refresh subject sections", command=self.refresh_subject_sections).pack(pady=(0, 8))
        self.update_subject_id(self.new_subject_name.get())

    def update_subject_id(self, selected_name):
        self.new_subject_id.delete(0, "end")
        self.new_subject_id.insert(0, PMT_SUBJECTS.get(selected_name, make_id(selected_name)))

    def refresh_task_list(self):
        self.task_list.configure(state="normal"); self.task_list.delete("1.0", "end")
        for number, task in enumerate(self.tasks, 1): self.task_list.insert("end", f"{number}. {self.format_task_display(task)}\n")
        self.task_list.configure(state="disabled")

    def add_task_gui(self):
        title, due, sid = self.task_entry.get().strip(), self.due_date_entry.get().strip(), self.subject_id_entry.get().strip()
        if not title or not due:
            messagebox.showerror("Error", "Please enter homework and a due date."); return
        try: datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD."); return
        if sid and not any(s.get("id") == sid for s in self.subjects):
            messagebox.showerror("Error", "That subject ID does not exist. Add the subject first."); return
        self.tasks.append({"due_date": due, "title": title, "subject_id": sid, "created_at": datetime.now().isoformat()})
        self.tasks.sort(key=task_sort_key); save_json(TASKS_FILE, self.tasks)
        self.task_entry.delete(0, "end"); self.due_date_entry.delete(0, "end"); self.refresh_task_list()

    def complete_task_gui(self):
        try:
            selected = self.task_list.get("sel.first", "sel.last")
            number = int(selected.split(".", 1)[0]) - 1
            if not 0 <= number < len(self.tasks): raise ValueError
            self.tasks.pop(number); save_json(TASKS_FILE, self.tasks); self.refresh_task_list()
        except (ValueError, TclError):
            messagebox.showwarning("Warning", "Please select a homework item to complete.")

    def clear_all_tasks(self):
        if messagebox.askyesno("Confirm", "Clear all homework?"):
            self.tasks.clear(); save_json(TASKS_FILE, self.tasks); self.refresh_task_list()

    def add_subject_gui(self):
        raw_id, name, board = self.new_subject_id.get().strip(), self.new_subject_name.get().strip(), str(self.exam_board_choice.get()).strip()
        sid = make_id(raw_id)
        if not raw_id or not sid or not name:
            messagebox.showerror("Error", "Please choose a subject name and enter a valid subject ID."); return
        if any(s.get("id") == sid for s in self.subjects):
            messagebox.showerror("Error", "That subject ID already exists."); return
        if not pmt_page_url(name, board):
            messagebox.showerror("Error", "Choose a subject and a supported exam board."); return
        notes = self.new_subject_notes.get().strip()
        links = [x.strip() for x in self.new_subject_links.get("1.0", "end").splitlines() if x.strip()]
        self.status_label.configure(text="Fetching PMT topics..."); self.add_subject_button.configure(state="disabled")
        threading.Thread(target=self.finish_subject_add, args=(sid, name, board, notes, links), daemon=True).start()

    def finish_subject_add(self, sid, name, board, notes, links):
        try:
            topics, url, error = (*fetch_pmt_topics(name, board), None)
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            topics, url = [], pmt_page_url(name, board)
        self.window.after(0, self.complete_subject_add, sid, name, board, notes, links, topics, url, error)

    def complete_subject_add(self, sid, name, board, notes, links, topics, url, error):
        self.add_subject_button.configure(state="normal")
        if error:
            self.status_label.configure(text="Could not fetch PMT topics")
            if not messagebox.askyesno("PMT unavailable", f"{error}\n\nAdd the subject without topics?"): return
        self.subjects.append({"id": sid, "name": name, "exam_board": board, "notes": notes, "links": links, "topics": topics, "pmt_url": url})
        save_json(SUBJECTS_FILE, self.subjects)
        self.new_subject_id.delete(0, "end"); self.new_subject_notes.delete(0, "end"); self.new_subject_links.delete("1.0", "end")
        self.status_label.configure(text=f"Added {len(topics)} PMT topics"); self.refresh_subject_sections()
        messagebox.showinfo("Success", f"Subject '{name}' added with {len(topics)} PMT topics.")

    def refresh_subject_sections(self):
        for child in self.subject_sections.winfo_children(): child.destroy()
        if not self.subjects:
            ctk.CTkLabel(self.subject_sections, text="Add a subject above to create its section.").pack(pady=20); return
        for subject in self.subjects:
            section = ctk.CTkFrame(self.subject_sections); section.pack(fill="x", padx=5, pady=6)
            ctk.CTkLabel(section, text=f"{subject.get('name', 'Subject')}  ({subject.get('exam_board') or 'No board'})", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(section, text=f"Subject ID: {subject.get('id', '')}", text_color="#aaaaaa").pack(anchor="w", padx=10)
            ctk.CTkLabel(section, text=f"Notes: {subject.get('notes') or 'None'}", wraplength=760, justify="left").pack(anchor="w", padx=10)
            names = "; ".join(t.get("name", "Unnamed topic") for t in subject.get("topics", []) if isinstance(t, dict))
            ctk.CTkLabel(section, text=f"Topics: {names or 'None'}", wraplength=760, justify="left").pack(anchor="w", padx=10, pady=2)
            if subject.get("pmt_url"):
                link = ctk.CTkLabel(section, text="Open PMT page", text_color="#55aaff"); link.pack(anchor="w", padx=10, pady=(0, 8)); link.bind("<Button-1>", lambda _, page=subject["pmt_url"]: webbrowser.open(page))


def main():
    window = ctk.CTk()
    StudyPlannerApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
