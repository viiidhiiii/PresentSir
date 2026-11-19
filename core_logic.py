"""
Component 2 - Core logic and functions
Owner: Kaushik M R (25BTRDC028)

Pure functions: numbers in, numbers out. No input() or files here,
which makes every rule easy to test on its own.
"""

import math

DEFAULT_THRESHOLD = 75


def attendance_percentage(attended, total):
    """Percentage of classes attended, rounded to 2 decimals. 0 classes -> 0.0"""
    if total == 0:
        return 0.0
    return round(attended / total * 100, 2)


def is_shortage(percentage, threshold=DEFAULT_THRESHOLD):
    """True when attendance is below the required threshold."""
    return percentage < threshold


def classes_needed(attended, total, threshold=DEFAULT_THRESHOLD):
    """How many classes in a row the student must attend to reach the threshold.

    Written recursively: if the student is already safe, 0 more classes
    are needed; otherwise attend one more class and ask the same question.
    """
    if total == 0 or attendance_percentage(attended, total) >= threshold:
        return 0
    return 1 + classes_needed(attended + 1, total + 1, threshold)


def classes_needed_formula(attended, total, threshold=DEFAULT_THRESHOLD):
    """Same answer in closed form, used to cross-check the recursive version.

    (attended + x) / (total + x) >= t   =>   x >= (t*total - attended) / (1 - t)
    """
    t = threshold / 100
    if total == 0 or attended / total >= t:
        return 0
    return math.ceil((t * total - attended) / (1 - t) - 1e-9)


def classes_can_skip(attended, total, threshold=DEFAULT_THRESHOLD):
    """How many upcoming classes a student can miss and still stay at or above the threshold."""
    skip = 0
    while attendance_percentage(attended, total + skip + 1) >= threshold:
        skip += 1
    return skip


def classes_text(n):
    """'1 class' / '5 classes'"""
    return f"{n} class" if n == 1 else f"{n} classes"


# lambda: turn a percentage into a status label
status_label = lambda pct, threshold=DEFAULT_THRESHOLD: (
    "SAFE" if pct >= threshold + 10 else "BORDERLINE" if pct >= threshold else "SHORTAGE"
)


def summarise(*records, **options):
    """Summarise any number of (usn, name, attended, total) records.

    *args   -> the records
    **kwargs -> threshold=75, only_shortage=False
    Returns a list of dicts sorted by percentage (lowest first).
    """
    threshold = options.get("threshold", DEFAULT_THRESHOLD)
    only_shortage = options.get("only_shortage", False)

    rows = []
    for usn, name, attended, total in records:
        pct = attendance_percentage(attended, total)
        if only_shortage and not is_shortage(pct, threshold):
            continue
        rows.append({
            "usn": usn,
            "name": name,
            "attended": attended,
            "total": total,
            "percentage": pct,
            "status": status_label(pct, threshold),
            "needed": classes_needed(attended, total, threshold),
            "can_skip": classes_can_skip(attended, total, threshold),
        })
    return sorted(rows, key=lambda r: r["percentage"])
