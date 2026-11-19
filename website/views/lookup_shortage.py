"""
PresentSir website (ADDITIONAL work, beyond the brief)
Student lookup and Shortage list pages.
Owner: Venkata Krishnan.S (25BTLDC001)

Each render_*() function draws one page. `app` carries the data loaded in website/app.py.
"""

import pandas as pd
import streamlit as st

import core_logic as core
import data_structures as ds
import visualisation as viz


def render_lookup(app):
    """Student lookup page."""
    students, register, threshold = app.students, app.register, app.threshold
    lookup, label = app.lookup, app.label

    st.title("Student lookup")
    usn = st.selectbox("Search a student", [u for u, _ in students], format_func=label,
                       placeholder="Type a roll number or name", index=None)
    if usn:
        attended, total = ds.student_counts(register, usn)
        pct = core.attendance_percentage(attended, total)
        status = core.status_label(pct, threshold)

        st.markdown(f"### {lookup[usn]} &nbsp; <span class='tag {status}'>{status}</span>", unsafe_allow_html=True)
        st.caption(usn)
        c1, c2, c3 = st.columns(3)
        c1.metric("Attendance", f"{pct}%")
        c2.metric("Classes attended", f"{attended} / {total}")
        if core.is_shortage(pct, threshold):
            c3.metric("Classes needed to recover", core.classes_needed(attended, total, threshold))
            st.error(f"Must attend the next {core.classes_text(core.classes_needed(attended, total, threshold))} "
                     f"in a row to reach {threshold}%.")
        else:
            c3.metric("Classes that can be missed", core.classes_can_skip(attended, total, threshold))
            st.success(f"Can miss {core.classes_text(core.classes_can_skip(attended, total, threshold))} "
                       f"and still stay at or above {threshold}%.")
        st.progress(min(pct / 100, 1.0))

        history = ds.student_history(register, usn)
        st.subheader("Every class day")
        st.markdown("<div class='strip'>" + "".join(
            f"<span class='{s}' title='{d} ({ds.weekday_of(d)}): {'Present' if s == 'P' else 'Absent'}'></span>"
            for d, s in history) + "</div>", unsafe_allow_html=True)
        st.caption("Green = present, red = absent. Hover a square to see the date.")

        absences = [d for d, s in history if s == "A"]
        if absences:
            with st.expander(f"Absent on {len(absences)} days"):
                st.write(", ".join(f"{d} ({ds.weekday_of(d)[:3]})" for d in absences))


def render_shortage(app):
    """Shortage list page."""
    threshold, records, dataframe, show = app.threshold, app.records, app.dataframe, app.show

    st.title(f"Students below {threshold}%")
    short = core.summarise(*records(), threshold=threshold, only_shortage=True)
    if not short:
        st.success(f"Everyone is at or above {threshold}%.")
    else:
        st.caption("**Classes needed** = classes in a row the student must attend to reach the threshold.")
        table = pd.DataFrame(short)[["usn", "name", "attended", "total", "percentage", "needed"]]
        st.dataframe(
            table, hide_index=True, width="stretch",
            column_config={
                "usn": "USN", "name": "Name", "attended": "Attended", "total": "Total",
                "percentage": st.column_config.ProgressColumn("Attendance", format="%.2f%%",
                                                              min_value=0, max_value=100),
                "needed": "Classes needed",
            })
        df = dataframe()
        show(viz.shortage_highlight(df, threshold, save=False))
