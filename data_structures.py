"""
Component 3 - Data structures
Owner: Nityasree Sriram Iyer (25BTRDC036)

The in-memory model of the class:

    students : list of tuples      [("25DEMO001", "Aarav Sharma"), ...]
    register : dict date -> set    {"2026-11-13": {"25DEMO001", "25DEMO004", ...}}
    lookup   : dict usn -> name    {"25DEMO001": "Aarav Sharma", ...}
    summary  : nested dict         {"25DEMO054": {"name": ..., "attended": 53, "total": 71, "percentage": 74.65}}
"""

from datetime import datetime

USN_PREFIX = "25DEMO"  # sample-data USNs, so no real student's USN is used


def build_lookup(students):
    """dict comprehension: USN -> name"""
    return {usn: name for usn, name in students}


def roll_of(usn):
    """Last 3 digits of a USN, e.g. '25DEMO054' -> '054'"""
    return usn[-3:]


def roll_map(students):
    """dict comprehension: roll number -> USN"""
    return {roll_of(usn): usn for usn, _ in students}


def next_usn(students):
    """Next free USN in the class sequence."""
    numbers = [int(roll_of(usn)) for usn, _ in students]
    return f"{USN_PREFIX}{(max(numbers) + 1 if numbers else 1):03d}"


def add_student(students, name):
    """Append a new (usn, name) tuple. Name is title-cased with string methods."""
    clean = " ".join(part.capitalize() for part in name.strip().split())
    usn = next_usn(students)
    students.append((usn, clean))
    return usn, clean


def search_students(students, query):
    """Find students whose USN or name contains the query (case-insensitive)."""
    q = query.strip().lower()
    return [(usn, name) for usn, name in students if q in usn.lower() or q in name.lower()]


def mark_day(register, day, all_usns, absent_usns):
    """Store one day: present = everyone minus the absentees (set difference)."""
    register[day] = set(all_usns) - set(absent_usns)
    return register[day]


def set_status(register, day, usn, present):
    """Change one student's mark on one date. Returns the old status ('P'/'A')."""
    old = "P" if usn in register[day] else "A"
    if present:
        register[day].add(usn)
    else:
        register[day].discard(usn)
    return old


def student_counts(register, usn):
    """(attended, total) for one student across every recorded date."""
    total = len(register)
    attended = sum(1 for present in register.values() if usn in present)
    return attended, total


def student_history(register, usn):
    """List of (date, 'P'/'A') in date order."""
    return [(day, "P" if usn in register[day] else "A") for day in sorted(register)]


def build_summary(students, register, pct_function):
    """Nested dictionary of every student's totals."""
    summary = {}
    for usn, name in students:
        attended, total = student_counts(register, usn)
        summary[usn] = {
            "name": name,
            "attended": attended,
            "total": total,
            "percentage": pct_function(attended, total),
        }
    return summary


def weekday_of(day):
    return datetime.strptime(day, "%Y-%m-%d").strftime("%A")


def weekdays_recorded(register):
    """set of distinct weekdays that have attendance."""
    return {weekday_of(day) for day in register}


def daily_counts(register):
    """list comprehension: (date, present count) in date order."""
    return [(day, len(register[day])) for day in sorted(register)]
