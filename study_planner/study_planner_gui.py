"""CustomTkinter interface. Run with: python -m study_planner.study_planner_gui"""
import threading
import webbrowser
from tkinter import messagebox
import customtkinter as ctk
from .pmt_service import PMT_BOARDS, PMT_SUBJECTS, fetch_pmt_topics, make_id, pmt_page_url
from .service import PlannerService


class StudyPlannerApp:
    def __init__(self, window: ctk.CTk) -> None:
        self.window, self.service = window, PlannerService(); window.title("Study Planner"); window.geometry("900x700"); window.minsize(750, 550); self.build_ui(); self.refresh()

    def build_ui(self) -> None:
        ctk.CTkLabel(self.window, text="Study Planner", font=("Arial", 24, "bold")).pack(pady=10)
        tabs = ctk.CTkTabview(self.window); tabs.pack(fill="both", expand=True, padx=20, pady=(0, 15)); home, subjects = tabs.add("Homework"), tabs.add("Subjects")
        form = ctk.CTkFrame(home); form.pack(fill="x", padx=10, pady=10)
        self.due = ctk.CTkEntry(form, placeholder_text="Due date YYYY-MM-DD", width=180); self.due.grid(row=0, column=0, padx=5, pady=5)
        self.subject = ctk.CTkEntry(form, placeholder_text="Subject ID (optional)", width=180); self.subject.grid(row=0, column=1, padx=5, pady=5)
        self.title = ctk.CTkEntry(form, placeholder_text="Homework title", width=350); self.title.grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(form, text="Add", command=self.add_task).grid(row=0, column=3, padx=5)
        self.task_list = ctk.CTkTextbox(home); self.task_list.pack(fill="both", expand=True, padx=10, pady=10); buttons = ctk.CTkFrame(home); buttons.pack(pady=8); ctk.CTkButton(buttons, text="Complete selected", command=self.complete_task).pack(side="left", padx=5); ctk.CTkButton(buttons, text="Clear all", fg_color="red", command=self.clear_tasks).pack(side="left", padx=5)
        subject_form = ctk.CTkFrame(subjects); subject_form.pack(fill="x", padx=10, pady=10)
        self.sid = ctk.CTkEntry(subject_form, placeholder_text="Subject ID", width=150); self.sid.grid(row=0, column=0, padx=5, pady=5)
        self.sname = ctk.CTkOptionMenu(subject_form, values=list(PMT_SUBJECTS)); self.sname.grid(row=0, column=1, padx=5, pady=5)
        self.board = ctk.CTkOptionMenu(subject_form, values=list(PMT_BOARDS)); self.board.grid(row=0, column=2, padx=5, pady=5)
        self.notes = ctk.CTkEntry(subject_form, placeholder_text="Notes", width=220); self.notes.grid(row=0, column=3, padx=5, pady=5); ctk.CTkButton(subject_form, text="Add subject", command=self.add_subject).grid(row=0, column=4, padx=5, pady=5)
        self.subject_list = ctk.CTkTextbox(subjects); self.subject_list.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh(self) -> None:
        self.task_list.configure(state="normal"); self.task_list.delete("1.0", "end")
        names = {s.id: s.name for s in self.service.subjects}
        for i, task in enumerate(self.service.tasks, 1): self.task_list.insert("end", f"{i}. {task.due_date} - [{names.get(task.subject_id, 'No subject')}] {task.title} ({task.display_status()})\n")
        self.task_list.configure(state="disabled"); self.subject_list.configure(state="normal"); self.subject_list.delete("1.0", "end")
        for subject in self.service.subjects: self.subject_list.insert("end", f"{subject.id}: {subject.name} ({subject.exam_board})\nTopics: {len(subject.topics)} | {subject.notes}\n\n")
        self.subject_list.configure(state="disabled")

    def add_task(self) -> None:
        try: self.service.add_task(self.title.get(), self.due.get(), self.subject.get()); self.title.delete(0, "end"); self.due.delete(0, "end"); self.refresh()
        except ValueError as error: messagebox.showerror("Invalid task", str(error))

    def complete_task(self) -> None:
        try:
            line = self.task_list.get("sel.first", "sel.last"); self.service.complete_task(int(line.split(".", 1)[0]) - 1); self.refresh()
        except Exception: messagebox.showwarning("Complete task", "Select a task line first.")

    def clear_tasks(self) -> None:
        if messagebox.askyesno("Confirm", "Clear all tasks?"): self.service.clear_tasks(); self.refresh()

    def add_subject(self) -> None:
        name, board = self.sname.get(), self.board.get(); sid = self.sid.get() or make_id(name)
        try: self.service.add_subject(sid, name, board, self.notes.get(), pmt_url=pmt_page_url(name, board) or ""); self.refresh(); threading.Thread(target=self.fetch_topics, args=(sid, name, board), daemon=True).start()
        except ValueError as error: messagebox.showerror("Invalid subject", str(error))

    def fetch_topics(self, sid: str, name: str, board: str) -> None:
        try:
            topics, url = fetch_pmt_topics(name, board); subject = next(s for s in self.service.subjects if s.id == sid); subject.topics, subject.pmt_url = topics, url; self.service.save(); self.window.after(0, self.refresh)
        except Exception: self.window.after(0, lambda: messagebox.showwarning("PMT unavailable", "Subject added, but topics could not be fetched."))


def main() -> None:
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue"); window = ctk.CTk(); StudyPlannerApp(window); window.mainloop()


if __name__ == "__main__": main()
