"""
Component 4 - Files and error handling
Owner: Vidhi Kataria (25BTRDC054)

    data/students.csv     usn,name
    data/attendance.csv   date,usn,name,status      (one row per student per day, P/A)
    data/settings.json    class name, threshold, working days

Every file is opened with `with open(...)`, and every failure is
turned into a clear message instead of a crash.
"""

import csv
import json
import os
from datetime import date, datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "class_name": "B.Tech CSE (Data Science) - Sem III - Section A",
    "subject": "Python Programming",
    "threshold": 75,
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
}


# ---------- custom exceptions ----------
class AttendanceError(Exception):
    """Base class for PresentSir errors."""


class DuplicateDateError(AttendanceError):
    """Attendance for this date has already been taken."""


class InvalidDateError(AttendanceError):
    """Date is in the future or on a non-working day."""


class UnknownStudentError(AttendanceError):
    """USN not found in the class list."""


# ---------- validation ----------
def validate_date(day, register, working_days):
    """Raise an error if the date cannot be used for marking attendance."""
    d = datetime.strptime(day, "%Y-%m-%d").date()
    if d > date.today():
        raise InvalidDateError(f"{day} is in the future - attendance can't be marked in advance.")
    weekday = d.strftime("%A")
    if weekday not in working_days:
        raise InvalidDateError(f"{day} is a {weekday}, which is not a working day.")
    if day in register:
        raise DuplicateDateError(f"Attendance for {day} has already been recorded.")
    return True


def check_recorded(day, register):
    """For editing: the date must already have attendance."""
    if day not in register:
        raise InvalidDateError(f"No attendance was taken on {day}, so there is nothing to edit.")
    return True


def check_usn(usn, lookup):
    if usn not in lookup:
        raise UnknownStudentError(f"No student with USN '{usn}'.")
    return usn


# ---------- settings (JSON) ----------
def load_settings(path=SETTINGS_FILE):
    try:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        print(f"  ! {os.path.basename(path)} not found - using default settings.")
        return dict(DEFAULT_SETTINGS)
    except json.JSONDecodeError:
        print(f"  ! {os.path.basename(path)} is corrupted - using default settings.")
        return dict(DEFAULT_SETTINGS)
    return {**DEFAULT_SETTINGS, **settings}  # fill in any missing keys


def save_settings(settings, path=SETTINGS_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ---------- students (CSV) ----------
def load_students(path=STUDENTS_FILE):
    """Return a list of (usn, name) tuples. Skips blank or broken rows."""
    students = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            for line_no, row in enumerate(csv.DictReader(f), start=2):
                try:
                    usn, name = row["usn"].strip(), row["name"].strip()
                    if not usn or not name:
                        raise ValueError("empty field")
                    students.append((usn, name))
                except (KeyError, AttributeError, ValueError):
                    print(f"  ! Skipping bad row {line_no} in {os.path.basename(path)}")
    except FileNotFoundError:
        print(f"  ! {os.path.basename(path)} not found - starting with an empty class.")
    return students


def save_students(students, path=STUDENTS_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["usn", "name"])
        writer.writerows(students)


# ---------- attendance (CSV) ----------
def load_attendance(path=ATTENDANCE_FILE):
    """Read the long-format CSV into {date: set(present USNs)}."""
    register = {}
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            for line_no, row in enumerate(csv.DictReader(f), start=2):
                try:
                    day = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date().isoformat()
                    status = row["status"].strip().upper()
                    if status not in ("P", "A"):
                        raise ValueError(f"status '{status}'")
                except (KeyError, AttributeError, ValueError) as err:
                    print(f"  ! Skipping bad row {line_no} in attendance.csv ({err})")
                    continue
                present = register.setdefault(day, set())
                if status == "P":
                    present.add(row["usn"].strip())
    except FileNotFoundError:
        print("  ! attendance.csv not found - no attendance recorded yet.")
    return register


def save_attendance(register, students, path=ATTENDANCE_FILE):
    """Write every day back to CSV, one row per student per day."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "usn", "name", "status"])
        for day in sorted(register):
            for usn, name in students:
                writer.writerow([day, usn, name, "P" if usn in register[day] else "A"])
    return sum(1 for _ in register) * len(students)
