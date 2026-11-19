"""
PresentSir - Smart Attendance Tracker
Group 05 | B.Tech CSE (Data Science) | Python Programming Group Project

Integration: ties the six components into one menu-driven program.
Owner: Kaushik M R (25BTRDC028)

Run:   python main.py
First run with no data?   python generate_data.py
"""

import menu_input as ui
import core_logic as core
import data_structures as ds
import files_errors as fe


class PresentSir:
    def __init__(self):
        self.settings = fe.load_settings()
        self.students = fe.load_students()      # list of (usn, name) tuples
        self.register = fe.load_attendance()    # {date: set of present USNs}
        self.unsaved = False

    @property
    def threshold(self):
        return self.settings["threshold"]

    def save(self):
        fe.save_students(self.students)
        rows = fe.save_attendance(self.register, self.students)
        fe.save_settings(self.settings)
        self.unsaved = False
        print(f"  Saved {len(self.students)} students and {rows} attendance rows.")

    # ---------- 1. mark attendance ----------
    def mark_attendance(self):
        if not self.students:
            print("  ! No students in the class yet. Add students first (option 7).")
            return
        day = ui.ask_date()
        try:
            fe.validate_date(day, self.register, self.settings["working_days"])
        except fe.DuplicateDateError as err:
            print(f"  ! {err}")
            if not ui.ask_yes_no("  Overwrite it"):
                return
        except fe.InvalidDateError as err:
            print(f"  ! {err}")
            return

        rolls = ds.roll_map(self.students)
        print(f"\nMarking {day} ({ds.weekday_of(day)}). Class strength: {len(self.students)}")
        absent_rolls = ui.ask_absent_rolls(rolls.keys())
        absent = {rolls[r] for r in absent_rolls}
        present = ds.mark_day(self.register, day, [u for u, _ in self.students], absent)

        print(f"  Present: {len(present)}   Absent: {len(absent)}")
        if absent:
            lookup = ds.build_lookup(self.students)
            print("  Absentees: " + ", ".join(f"{lookup[u]} ({ds.roll_of(u)})" for u in sorted(absent)))
        self.save()

        # early warning: anyone absent today who has now dropped below the threshold
        for usn in sorted(absent):
            attended, total = ds.student_counts(self.register, usn)
            pct = core.attendance_percentage(attended, total)
            if core.is_shortage(pct, self.threshold):
                print(f"  ALERT {ds.build_lookup(self.students)[usn]} is at {pct}% "
                      f"- needs {core.classes_text(core.classes_needed(attended, total, self.threshold))} to recover.")

    # ---------- 2. edit one record ----------
    def edit_record(self):
        day = ui.ask_date("Date to edit (YYYY-MM-DD): ")
        try:
            fe.check_recorded(day, self.register)
        except fe.InvalidDateError as err:
            print(f"  ! {err}")
            return
        picked = self.pick_student()
        if not picked:
            return
        usn, name = picked

        current = "P" if usn in self.register[day] else "A"
        before = core.attendance_percentage(*ds.student_counts(self.register, usn))
        word = {"P": "PRESENT", "A": "ABSENT"}
        new = "A" if current == "P" else "P"
        print(f"  {name} is marked {word[current]} on {day} ({ds.weekday_of(day)}).")
        if not ui.ask_yes_no(f"  Change it to {word[new]}"):
            print("  No change made.")
            return

        ds.set_status(self.register, day, usn, present=(new == "P"))
        self.save()
        after = core.attendance_percentage(*ds.student_counts(self.register, usn))
        print(f"  Updated. {name}: {before}% -> {after}%")

    # ---------- 3. view one student ----------
    def pick_student(self):
        """Ask for a USN, roll number or name and return one (usn, name), or None."""
        query = ui.ask_text("Enter USN, roll number or part of the name: ")
        matches = self.find(query)
        if not matches:
            print(f"  ! No student matches '{query}'.")
            return None
        if len(matches) > 1:
            print("  Several matches:")
            for i, (usn, name) in enumerate(matches, start=1):
                print(f"   {i}. {usn}  {name}")
            matches = [matches[ui.ask_int("  Pick a number: ", 1, len(matches)) - 1]]
        return matches[0]

    def view_student(self):
        picked = self.pick_student()
        if not picked:
            return
        usn, name = picked

        attended, total = ds.student_counts(self.register, usn)
        pct = core.attendance_percentage(attended, total)
        print(f"\n  {name}  ({usn})")
        print(f"  Attended {attended} of {total} classes  ->  {pct}%   [{core.status_label(pct, self.threshold)}]")
        if core.is_shortage(pct, self.threshold):
            print(f"  Must attend the next {core.classes_text(core.classes_needed(attended, total, self.threshold))} "
                  f"in a row to reach {self.threshold}%.")
        else:
            print(f"  Can miss {core.classes_text(core.classes_can_skip(attended, total, self.threshold))} "
                  f"and still stay at or above {self.threshold}%.")

        history = ds.student_history(self.register, usn)
        recent = history[-10:]
        if recent:
            print("  Last 10 classes: " + "  ".join(f"{d[5:]}:{s}" for d, s in recent))
        absences = [d for d, s in history if s == "A"]
        if absences:
            print(f"  Absent on {len(absences)} days, most recent: {', '.join(absences[-5:])}")

        if history and ui.ask_yes_no("  Save a chart of this student's attendance"):
            import analysis
            import visualisation
            print(f"  saved  {visualisation.student_report(analysis.load_dataframe(), usn, self.threshold)}")

    def find(self, query):
        q = query.strip()
        if q.isdigit():
            usn = ds.roll_map(self.students).get(q.zfill(3))
            return [(usn, ds.build_lookup(self.students)[usn])] if usn else []
        return ds.search_students(self.students, q)

    # ---------- 4. class register ----------
    def view_register(self):
        if not self.register:
            print("  ! No attendance recorded yet.")
            return
        days = sorted(self.register)
        print(f"\n  {len(days)} class days recorded ({days[0]} to {days[-1]})")
        print(f"  {'Date':<12}{'Day':<11}{'Present':>8}{'Absent':>8}{'%':>8}")
        for day, count in ds.daily_counts(self.register)[-15:]:
            pct = core.attendance_percentage(count, len(self.students))
            print(f"  {day:<12}{ds.weekday_of(day):<11}{count:>8}{len(self.students) - count:>8}{pct:>8}")
        if len(days) > 15:
            print("  (showing the last 15 days)")

        if ui.ask_yes_no("\n  Show who was absent on a specific date"):
            day = ui.ask_date("  Date (YYYY-MM-DD): ")
            if day not in self.register:
                print(f"  ! No attendance recorded on {day}.")
                return
            absent = [(u, n) for u, n in self.students if u not in self.register[day]]
            print(f"  Absent on {day}: {len(absent)}")
            for usn, name in absent:
                print(f"    {ds.roll_of(usn)}  {name}")

    # ---------- 5. shortage list ----------
    def shortage_list(self):
        records = [(usn, name, *ds.student_counts(self.register, usn)) for usn, name in self.students]
        short = core.summarise(*records, threshold=self.threshold, only_shortage=True)
        if not short:
            print(f"  Everyone is at or above {self.threshold}%.")
            return
        print(f"\n  {len(short)} students below {self.threshold}%:")
        print(f"  {'USN':<12}{'Name':<22}{'Att/Total':>10}{'%':>8}{'Need':>6}")
        for r in short:
            print(f"  {r['usn']:<12}{r['name']:<22}{str(r['attended']) + '/' + str(r['total']):>10}"
                  f"{r['percentage']:>8}{r['needed']:>6}")
        print("  'Need' = classes in a row the student must attend to reach the threshold.")

    # ---------- 6. search ----------
    def search(self):
        query = ui.ask_text("Search USN or name: ")
        results = ds.search_students(self.students, query)
        if not results:
            print(f"  ! Nothing matches '{query}'.")
            return
        summary = ds.build_summary(self.students, self.register, core.attendance_percentage)
        for usn, name in results:
            pct = summary[usn]["percentage"]
            print(f"  {usn}  {name:<22} {pct:>6}%  {core.status_label(pct, self.threshold)}")

    # ---------- 7. add student ----------
    def add_student(self):
        name = ui.ask_text("Full name of the new student: ", min_length=2)
        if not name.replace(" ", "").replace(".", "").isalpha():
            print("  ! Names can only contain letters, spaces and dots.")
            return
        usn, clean = ds.add_student(self.students, name)
        print(f"  Added {clean} with USN {usn}. Earlier days will count as absent.")
        self.save()

    # ---------- 8. analysis ----------
    def run_analysis(self):
        import analysis
        if not self.register:
            print("  ! No attendance data to analyse yet.")
            return
        try:
            analysis.print_report(analysis.load_dataframe(), self.threshold)
        except (FileNotFoundError, KeyError) as err:
            print(f"  ! Could not run the analysis: {err}")

    # ---------- 9. charts ----------
    def make_charts(self):
        import analysis
        import visualisation
        if not self.register:
            print("  ! No attendance data to chart yet.")
            return
        print("  Generating charts...")
        for path in visualisation.generate_all(analysis.load_dataframe(), self.threshold):
            print(f"   saved  {path}")

    # ---------- 10. settings ----------
    def change_settings(self):
        print(f"  Class     : {self.settings['class_name']}")
        print(f"  Threshold : {self.threshold}%")
        print(f"  Work days : {', '.join(self.settings['working_days'])}")
        if ui.ask_yes_no("  Change the required attendance %"):
            self.settings["threshold"] = ui.ask_int("  New threshold (50-100): ", 50, 100)
        if ui.ask_yes_no("  Toggle Saturday as a working day"):
            days = self.settings["working_days"]
            if "Saturday" in days:
                days.remove("Saturday")
            else:
                days.append("Saturday")
        fe.save_settings(self.settings)
        print("  Settings saved.")

    # ---------- main loop ----------
    def run(self):
        ui.show_banner(self.settings["class_name"])
        print(f"   {len(self.students)} students | {len(self.register)} class days | "
              f"required {self.threshold}%")
        actions = {
            "1": self.mark_attendance, "2": self.edit_record, "3": self.view_student,
            "4": self.view_register, "5": self.shortage_list, "6": self.search,
            "7": self.add_student, "8": self.run_analysis, "9": self.make_charts,
            "10": self.change_settings,
        }
        while True:
            ui.show_menu()
            choice = ui.get_choice()
            if choice == "0":
                self.save()
                print("  Goodbye!")
                break
            try:
                actions[choice]()
            except fe.AttendanceError as err:
                print(f"  ! {err}")
            except KeyboardInterrupt:
                print("\n  Cancelled.")
                continue


if __name__ == "__main__":
    try:
        PresentSir().run()
    except (KeyboardInterrupt, EOFError):
        print("\n  Exiting PresentSir.")
