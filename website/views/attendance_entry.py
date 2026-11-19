"""
PresentSir website (ADDITIONAL work, beyond the brief)
Mark attendance (roll call or quick entry) and Edit a record pages: how the teacher enters
and corrects attendance.
Owner: Alicia Jogy (25BTRDC006)

Each render_*() function draws one page. `app` carries the data loaded in website/app.py.
"""

from datetime import date

import pandas as pd
import streamlit as st

import core_logic as core
import data_structures as ds
import files_errors as fe


def render_mark(app):
    """Mark attendance page."""
    settings, students, register = app.settings, app.students, app.register
    threshold, lookup, label = app.threshold, app.lookup, app.label

    st.title("Mark attendance")

    day = st.date_input("Date", value=date.today(), max_value=date.today(), format="YYYY-MM-DD").isoformat()

    can_mark, overwrite = True, False
    try:
        fe.validate_date(day, register, settings["working_days"])
    except fe.DuplicateDateError as err:
        st.warning(f"{err}")
        overwrite = st.checkbox("Overwrite the existing attendance for this date")
        can_mark = overwrite
    except fe.InvalidDateError as err:
        st.error(f"{err}")
        can_mark = False

    if can_mark:
        default_absent = []
        if overwrite:
            default_absent = [usn for usn, _ in students if usn not in register[day]]

        mode = st.radio("How do you want to mark?",
                        ["Roll call: go down the class list", "Quick: type only the absentees"],
                        horizontal=True)

        if mode.startswith("Roll call"):
            st.caption("Everyone starts ticked as present. Call each name and **untick** anyone who doesn't answer.")
            roll = pd.DataFrame({
                "Roll": [ds.roll_of(usn) for usn, _ in students],
                "Name": [name for _, name in students],
                "Present": [usn not in default_absent for usn, _ in students],
            })
            edited = st.data_editor(
                roll, hide_index=True, width="stretch", height=460,
                key=f"rollcall-{day}-{overwrite}",
                disabled=["Roll", "Name"],
                column_config={"Present": st.column_config.CheckboxColumn("Present", width="small")},
            )
            absent = [usn for (usn, _), here in zip(students, edited["Present"]) if not here]
        else:
            st.caption("Everyone is marked present by default. Pick only the students who are **absent**.")
            absent = st.multiselect(f"Absent on {day} ({ds.weekday_of(day)})",
                                    options=[usn for usn, _ in students], default=default_absent,
                                    format_func=label, placeholder="Search by roll number or name")

        c1, c2, _ = st.columns([1, 1, 3])
        c1.metric("Present", len(students) - len(absent))
        c2.metric("Absent", len(absent))
        if absent and mode.startswith("Roll call"):
            st.caption("Absent: " + ", ".join(label(u) for u in absent))
        submitted = st.button("Save attendance", type="primary")

        if submitted:
            ds.mark_day(register, day, [u for u, _ in students], absent)
            fe.save_attendance(register, students)
            st.success(f"Saved {day}: {len(students) - len(absent)} present, {len(absent)} absent.")
            for usn in absent:
                attended, total = ds.student_counts(register, usn)
                pct = core.attendance_percentage(attended, total)
                if core.is_shortage(pct, threshold):
                    st.error(f"**{lookup[usn]}** is now at {pct}%: needs "
                             f"{core.classes_text(core.classes_needed(attended, total, threshold))} in a row to recover.")


def render_edit(app):
    """Edit a record page."""
    students, register, lookup, label = app.students, app.register, app.lookup, app.label

    st.title("Edit a record")
    st.caption("Fix one student's mark on one date without re-marking the whole day.")
    if not register:
        st.info("No attendance recorded yet.")
        st.stop()

    left, right = st.columns(2)
    day = left.selectbox("Date", sorted(register, reverse=True),
                         format_func=lambda d: f"{d} ({ds.weekday_of(d)})")
    usn = right.selectbox("Student", [u for u, _ in students], format_func=label, index=None,
                          placeholder="Type a roll number or name")
    if usn:
        current = "Present" if usn in register[day] else "Absent"
        before = core.attendance_percentage(*ds.student_counts(register, usn))
        st.markdown(f"**{lookup[usn]}** is currently marked **{current}** on {day}.")
        new = st.radio("Change to", ["Present", "Absent"], index=0 if current == "Present" else 1,
                       horizontal=True)
        if st.button("Save change", type="primary", disabled=(new == current)):
            ds.set_status(register, day, usn, present=(new == "Present"))
            fe.save_attendance(register, students)
            after = core.attendance_percentage(*ds.student_counts(register, usn))
            st.success(f"Updated {lookup[usn]} on {day}: {current} → {new}. "
                       f"Attendance {before}% → {after}%.")
        elif new == current:
            st.caption("Pick the other option to make a change.")
