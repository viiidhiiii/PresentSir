# PresentSir: Smart Attendance Tracker

**Group 05 · B.Tech CSE (Data Science) · Semester III · Python Programming Group Project**

Paper attendance registers make it hard to know which students are falling below the required 75%. PresentSir marks daily attendance for a class, works out every student's attendance percentage and flags shortages early, including how many classes in a row a student must attend to recover.

This repository has two parts:

| | What it is | Where it is |
|---|---|---|
| **Part A: Required project** | The menu-driven Python program asked for in the brief, its six components, data, charts and presentation | Repository root (`main.py`, the six component files, `data/`, `charts/`, the PPT) |
| **Part B: Additional work** | A website version of the same program, built on top of Part A's components | `website/` folder only |

Part B is extra work beyond the brief. Part A runs on its own and does not need anything from Part B.

## Team

| # | Name | USN |
|---|---|---|
| 1 | Alicia Jogy | 25BTRDC006 |
| 2 | Kaushik M R | 25BTRDC028 |
| 3 | Nityasree Sriram Iyer | 25BTRDC036 |
| 4 | Vidhi Kataria | 25BTRDC054 |
| 5 | Vishal Tejas | 25BTRDC055 |
| 6 | Venkata Krishnan.S | 25BTLDC001 |

---

# Part A: Required project

## How to run

```bash
pip install -r requirements.txt
python main.py
```

The repository already includes sample data (60 students × 71 class days = **4,260 records**). To regenerate it: `python generate_data.py`. Sample students have made-up USNs (`25DEMO001` to `25DEMO060`) so that no real student's USN is used.

## Main menu

```
[1] Mark attendance for a date              [6]  Search a student by USN or name
[2] Edit a record (one student, one date)   [7]  Add a new student
[3] View a student's attendance             [8]  Data analysis report
[4] View the class register (date-wise)     [9]  Generate charts
[5] Shortage list (below required %)        [10] Settings
                                            [0]  Save and exit
```

To mark attendance, type only the **absent** roll numbers (the last 3 digits of the USN, e.g. `5, 23, 54`), or press Enter if everyone is present.

## Components and contributions

Each member owns one of the six components from the brief, plus one shared task.

| Component (from the brief) | File | What it contains | Owner |
|---|---|---|---|
| 1. Menu, input and validation | `menu_input.py` | Menu display, `get_choice`, `ask_date`, `ask_int`, `ask_yes_no`, `ask_absent_rolls`; every input re-asked until valid | **Alicia Jogy** |
| 2. Core logic and functions | `core_logic.py` | `attendance_percentage`, `is_shortage`, recursive `classes_needed` (checked against a formula), `classes_can_skip`, `summarise(*records, **options)`, `status_label` lambda | **Kaushik M R** |
| 3. Data structures | `data_structures.py` | Class list as tuples, `register` dict of date → set of present USNs, lookup and roll-number dicts (comprehensions), `mark_day` (set difference), `set_status`, `search_students`, nested summary dict | **Nityasree Sriram Iyer** |
| 4. Files and error handling | `files_errors.py` | CSV and JSON load/save with `with open`, custom exceptions `DuplicateDateError`, `InvalidDateError`, `UnknownStudentError`, `validate_date`, safe handling of missing or broken files | **Vidhi Kataria** |
| 5. Data analysis | `analysis.py` | pandas `merge`, `groupby`, `fillna`, `pivot_table`, `concat`; student-wise, date-wise, weekday and monthly patterns; NumPy shortage list; per-student timeline | **Vishal Tejas** |
| 6. Visualisation and report | `visualisation.py` | Four labelled matplotlib charts, including a 2×2 subplots dashboard, plus a per-student report chart | **Venkata Krishnan.S** |

| Shared task | Files | Owner |
|---|---|---|
| Presentation | `PresentSir_Presentation.pptx` | **Alicia Jogy** |
| Integration: one menu-driven program using all six components | `main.py` | **Kaushik M R** |
| Project documentation | `README.md` | **Nityasree Sriram Iyer** |
| Repository setup | `requirements.txt`, `.gitignore`, GitHub repo and permissions | **Vidhi Kataria** |
| Sample data generation (100+ records) | `generate_data.py`, `data/` | **Vishal Tejas** |
| Generated charts | `charts/*.png` | **Venkata Krishnan.S** |

## Data files (`data/`)

| File | Columns | Records |
|---|---|---|
| `students.csv` | `usn, name` | 60 |
| `attendance.csv` | `date, usn, name, status` (P/A) | 4,260 |
| `settings.json` | `class_name, subject, threshold, working_days` | 1 object |

## Key logic

**Classes needed to reach 75%.** If a student has attended `A` of `T` classes, they need `x` consecutive classes where `(A + x) / (T + x) ≥ 0.75`. `classes_needed()` solves this recursively (attend one more class, check again). It is cross-checked against the closed-form answer `⌈(0.75T − A) / 0.25⌉` for every valid `(A, T)` up to 70 classes.

## Error handling

| Situation | Exception | What happens |
|---|---|---|
| Menu choice `11`, roll number `abc` | `ValueError` | Message shown, asks again |
| A data file is missing | `FileNotFoundError` | Starts empty or loads default settings |
| `settings.json` is corrupted | `json.JSONDecodeError` | Falls back to default settings |
| Date already marked | `DuplicateDateError` (custom) | Asks whether to overwrite |
| Future date, Saturday/Sunday | `InvalidDateError` (custom) | Explains why, returns to the menu |
| Editing a date with no attendance | `InvalidDateError` (custom) | Explains there is nothing to edit |
| Bad row in a CSV | `KeyError` / `ValueError` | Row skipped with a warning |

## Charts (`charts/`)

1. `attendance_percentage_bar.png`: every student's %, coloured shortage / borderline / safe
2. `daily_present_line.png`: present count per day with a 5-day rolling average
3. `shortage_highlight.png`: students below 75% and the classes each needs to recover
4. `dashboard_subplots.png`: 2×2 subplots of weekday average, distribution, status split and monthly average
5. `student_<USN>.png` (from menu option 3, on request): one student's running %, month-by-month and weekday charts

## What the sample data shows

- 8 of 60 students are below 75%; 3 of them need 40+ classes in a row to recover.
- Fridays (79.0%) and Mondays (80.4%) trail the midweek days (about 86%).
- The class average slid from 86.1% in September to 81.5% in November.

---

# Part B: Additional work (website)

**Live website:** https://presentsir-agjfasqntqpurihzjyfbwk.streamlit.app/

This goes beyond what the brief asked for. It is a website for the same program, written in Python with [Streamlit](https://streamlit.io). It **imports Part A's six components** instead of copying them, so the website and `main.py` share the same logic and the same data files: attendance marked in one shows up in the other.

## How to run

From the repository root:

```bash
pip install -r requirements.txt
streamlit run website/app.py
```

It opens at `http://localhost:8501`. The sidebar has two modes:

- **Teacher:** Dashboard, Mark attendance, Edit a record, Student lookup, Shortage list, Class register, Analysis report and Manage class.
- **Student:** log in with a USN and full name to see only your own attendance: your %, how many classes you need or can miss, a running-% chart, month-by-month and weekday charts, and a table of every class. Demo login: `25DEMO054` / `Rachana Iyer`.

The student login checks the USN and name against the class list. It keeps each student in their own view, but it is not real password security.

**Free public link:** sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub, click **Create app**, pick this repository, set the main file to `website/app.py` and click **Deploy**. Attendance marked on the hosted site is kept only until the app restarts.

## Website contributions

| File | Pages | Owner |
|---|---|---|
| `website/views/attendance_entry.py` | Mark attendance, Edit a record | **Alicia Jogy** |
| `website/views/student_portal.py` | Student login and personal attendance view | **Kaushik M R** |
| `website/views/register_manage.py` | Class register, Manage class | **Nityasree Sriram Iyer** |
| `website/app.py`, `website/views/__init__.py`, `.streamlit/config.toml` | App shell: data loading, sidebar, Teacher/Student switch, page routing, theme | **Vidhi Kataria** |
| `website/views/overview.py` | Dashboard, Analysis report | **Vishal Tejas** |
| `website/views/lookup_shortage.py` | Student lookup, Shortage list | **Venkata Krishnan.S** |

---

# Contribution summary

| Member | Part A: component | Part A: shared task | Part B: website |
|---|---|---|---|
| Alicia Jogy (25BTRDC006) | Menu, input and validation (`menu_input.py`) | Presentation | Mark attendance, Edit a record |
| Kaushik M R (25BTRDC028) | Core logic and functions (`core_logic.py`) | Integration (`main.py`) | Student login and portal |
| Nityasree Sriram Iyer (25BTRDC036) | Data structures (`data_structures.py`) | README | Class register, Manage class |
| Vidhi Kataria (25BTRDC054) | Files and error handling (`files_errors.py`) | Repository setup | App shell and navigation |
| Vishal Tejas (25BTRDC055) | Data analysis (`analysis.py`) | Sample data (`generate_data.py`, `data/`) | Dashboard, Analysis report |
| Venkata Krishnan.S (25BTLDC001) | Visualisation and report (`visualisation.py`) | Generated charts (`charts/`) | Student lookup, Shortage list |

# Repository structure

```
PresentSir/
│   ── Part A: required ──────────────────────────────
├── main.py                      menu-driven program (run this)
├── menu_input.py                component 1
├── core_logic.py                component 2
├── data_structures.py           component 3
├── files_errors.py              component 4
├── analysis.py                  component 5
├── visualisation.py             component 6
├── generate_data.py             creates the sample data
├── data/
│   ├── students.csv
│   ├── attendance.csv
│   └── settings.json
├── charts/                      PNG charts (menu option 9)
├── PresentSir_Presentation.pptx
├── requirements.txt
├── README.md
│
│   ── Part B: additional ────────────────────────────
├── website/
│   ├── app.py                   streamlit run website/app.py
│   └── views/                   one file per group of pages
└── .streamlit/config.toml       website theme
```
