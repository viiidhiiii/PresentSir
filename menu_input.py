"""
Component 1 - Menu, input and validation
Owner: Alicia Jogy (25BTRDC006)

Everything the user types goes through a function in this file.
Each function keeps asking until it gets a valid value, so the rest
of the program never has to deal with bad input.
"""

from datetime import date, datetime

MENU_OPTIONS = {
    "1": "Mark attendance for a date",
    "2": "Edit a record (one student, one date)",
    "3": "View a student's attendance",
    "4": "View the class register (date-wise)",
    "5": "Shortage list (below required %)",
    "6": "Search a student by USN or name",
    "7": "Add a new student",
    "8": "Data analysis report",
    "9": "Generate charts",
    "10": "Settings",
    "0": "Save and exit",
}

LINE = "=" * 52


def show_banner(class_name):
    print("\n" + LINE)
    print("   PresentSir  |  Smart Attendance Tracker")
    print(f"   Class: {class_name}")
    print(LINE)


def show_menu():
    print("\n" + "-" * 52)
    print("  MAIN MENU")
    print("-" * 52)
    for key, label in MENU_OPTIONS.items():
        print(f"  [{key}]{' ' if len(key) == 1 else ''} {label}")
    print("-" * 52)


def get_choice(prompt="Enter your choice: ", valid=None):
    """Return a menu key. Keeps asking until the key is valid."""
    valid = valid or MENU_OPTIONS.keys()
    while True:
        choice = input(prompt).strip()
        if choice in valid:
            return choice
        numbers = sorted(int(k) for k in valid)
        print(f"  ! '{choice}' is not a valid option. Choose from {numbers[0]}-{numbers[-1]}.")


def ask_int(prompt, low=None, high=None):
    """Ask for a whole number within [low, high]."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"  ! '{raw}' is not a whole number. Try again.")
            continue
        if low is not None and value < low:
            print(f"  ! Must be at least {low}.")
            continue
        if high is not None and value > high:
            print(f"  ! Must be at most {high}.")
            continue
        return value


def ask_date(prompt="Date (YYYY-MM-DD, Enter = today): "):
    """Ask for a date. Blank means today. Returns a 'YYYY-MM-DD' string.

    Format errors are caught here; rules such as 'no future dates'
    are checked by files_errors.validate_date().
    """
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return date.today().isoformat()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print(f"  ! '{raw}' is not a valid date. Use the format YYYY-MM-DD, e.g. 2026-11-18.")


def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ! Please type y or n.")


def ask_text(prompt, min_length=1):
    while True:
        text = input(prompt).strip()
        if len(text) >= min_length:
            return text
        print(f"  ! Please enter at least {min_length} character(s).")


def ask_absent_rolls(valid_rolls):
    """Ask for absent roll numbers as a comma-separated list.

    The user can type the last digits of the USN (e.g. 7, 12, 054).
    Returns a set of roll strings ('007', '012', '054').
    Blank input means everyone is present.
    """
    while True:
        raw = input("Absent roll numbers, comma-separated (Enter = all present): ").strip()
        if raw == "":
            return set()
        parts = [p.strip() for p in raw.replace(" ", ",").split(",") if p.strip()]
        bad = [p for p in parts if not p.isdigit()]
        if bad:
            print(f"  ! Not numbers: {', '.join(bad)}. Try again.")
            continue
        rolls = {p.zfill(3) for p in parts}
        unknown = sorted(rolls - set(valid_rolls))
        if unknown:
            print(f"  ! No student with roll number(s): {', '.join(unknown)}. Try again.")
            continue
        return rolls


def pause():
    input("\nPress Enter to return to the menu...")
