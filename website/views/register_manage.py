"""
PresentSir website (ADDITIONAL work, beyond the brief)
Class register and Manage class pages.
Owner: Nityasree Sriram Iyer (25BTRDC036)

Each render_*() function draws one page. `app` carries the data loaded in website/app.py.
"""

import pandas as pd
import streamlit as st

import analysis
import core_logic as core
import data_structures as ds
import files_errors as fe


def render_register(app):
    """Class register page."""
    students, register, dataframe = app.students, app.register, app.dataframe

    st.title("Class register")
    if not register:
        st.info("No attendance recorded yet.")
        st.stop()

    rows = [{"Date": d, "Day": ds.weekday_of(d), "Present": c, "Absent": len(students) - c,
             "Attendance": core.attendance_percentage(c, len(students))}
            for d, c in ds.daily_counts(register)]
    reg = pd.DataFrame(rows).iloc[::-1]

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Date-wise")
        st.dataframe(reg, hide_index=True, width="stretch", height=420,
                     column_config={"Attendance": st.column_config.ProgressColumn(
                         "Attendance", format="%.1f%%", min_value=0, max_value=100)})
    with right:
        st.subheader("Who was absent?")
        day = st.selectbox("Pick a date", reg["Date"].tolist())
        gone = [(u, n) for u, n in students if u not in register[day]]
        st.caption(f"{len(gone)} absent on {day} ({ds.weekday_of(day)})")
        st.dataframe(pd.DataFrame(gone, columns=["USN", "Name"]), hide_index=True,
                     width="stretch", height=340)

    st.subheader("Full register")
    grid = analysis.register_matrix(dataframe())
    st.caption("1 = present, 0 = absent. Scroll sideways to see every date.")
    st.dataframe(grid.style.map(lambda v: "background-color:#D9F0E4" if v else "background-color:#F8D7D7"),
                 width="stretch", height=420)


def render_manage(app):
    """Manage class page."""
    settings, students, register, threshold = app.settings, app.students, app.register, app.threshold

    st.title("Manage class")

    left, right = st.columns(2)
    with left:
        st.subheader("Add a student")
        with st.form("add", clear_on_submit=True):
            name = st.text_input("Full name")
            if st.form_submit_button("Add student", type="primary"):
                if len(name.strip()) < 2 or not name.replace(" ", "").replace(".", "").isalpha():
                    st.error("Names can only contain letters, spaces and dots.")
                else:
                    new_usn, clean = ds.add_student(students, name)
                    fe.save_students(students)
                    fe.save_attendance(register, students)
                    st.success(f"Added {clean} with USN {new_usn}. Earlier days count as absent.")

    with right:
        st.subheader("Settings")
        with st.form("settings"):
            new_threshold = st.slider("Required attendance %", 50, 100, threshold)
            saturday = st.checkbox("Saturday is a working day", "Saturday" in settings["working_days"])
            if st.form_submit_button("Save settings"):
                settings["threshold"] = new_threshold
                days = [d for d in settings["working_days"] if d != "Saturday"]
                settings["working_days"] = days + (["Saturday"] if saturday else [])
                fe.save_settings(settings)
                st.success("Settings saved.")
                st.rerun()

    st.subheader("Download the data files")
    c1, c2, c3 = st.columns(3)
    for col, path, mime in ((c1, fe.STUDENTS_FILE, "text/csv"), (c2, fe.ATTENDANCE_FILE, "text/csv"),
                            (c3, fe.SETTINGS_FILE, "application/json")):
        try:
            with open(path, "rb") as f:
                col.download_button(path.split("/")[-1].split("\\")[-1], f.read(),
                                    file_name=path.split("/")[-1].split("\\")[-1], mime=mime,
                                    width="stretch")
        except FileNotFoundError:
            col.caption(f"{path} not found")
