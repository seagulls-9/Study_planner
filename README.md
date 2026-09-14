# Study Planner 📚

A Python task manager for students. Keep track of your assignments, projects, and study goals with automatic deadline tracking.

**Two versions:** CLI for quick access, modern GUI for daily use.

## Features

- ✅ Add tasks with due dates
- ✅ See days remaining (or overdue alerts)
- ✅ Mark tasks as done
- ✅ Auto-sorts by deadline
- ✅ Everything saves automatically

## Quick Start

### GUI Version (Recommended)

```bash
pip install customtkinter
python study_planner/study_planner_gui.py
```

Just fill in your task and due date, click "Add Task", and you're done. Tasks show how many days you have left.

### CLI Version

```bash
python study_planner/study_planner.py
```

Menu-based interface. Choose 1-5 to manage your tasks.

## How It Works

1. **Add a task** → enter description + due date (YYYY-MM-DD)
2. **View tasks** → see everything sorted by deadline with days remaining
3. **Complete task** → select it and mark as done
4. **That's it** → everything syncs to `tasks.txt`

## Task Display

```
1. 2024-12-25 - Study Python (10 days left)
2. 2024-12-20 - Complete Assignment (OVERDUE by 5 days)
3. 2024-12-30 - Review Notes (Due TODAY)
```

## What I Learned

Building this taught me:
- File I/O and data persistence
- Date handling and calculations
- GUI development with tkinter & CustomTkinter
- Input validation and error handling
- CLI design patterns
- Clean code organization

## Tech Stack

- Python 3.7+
- CustomTkinter (modern GUI)
- Datetime (for scheduling)
- Plain text storage (simple & reliable)

## Future Ideas

- Task priorities
- Categories (Math, English, etc.)
- Notifications
- Dark/light theme toggle
- Mobile app

---

Made by [@seagulls-9](https://github.com/seagulls-9) while learning Python 🚀
