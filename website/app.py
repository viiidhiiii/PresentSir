"""
PresentSir website (ADDITIONAL work, beyond the brief)
App shell: page setup, styling, data loading, sidebar, Teacher/Student switch and page routing.
Owner: Vidhi Kataria (25BTRDC054)

The required project is main.py and the six component files in the repository root.
This website is an extra front end on top of those same components: it imports
them, so the logic and data files are shared with main.py.

Run from the repository root:
    pip install -r requirements.txt
    streamlit run website/app.py
"""

import os
import sys
from types import SimpleNamespace

# make the repository root importable (core_logic.py, analysis.py, ...)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib.pyplot as plt  # noqa: E402
import streamlit as st  # noqa: E402

import analysis  # noqa: E402
import data_structures as ds  # noqa: E402
import files_errors as fe  # noqa: E402
from views import attendance_entry, lookup_shortage, overview, register_manage, student_portal  # noqa: E402

st.set_page_config(page_title="PresentSir · Smart Attendance Tracker", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 2.2rem; max-width: 1250px;}
  [data-testid="stMetric"] {background: #F4F7FB; border: 1px solid #E3E8F0; border-radius: 12px; padding: 14px 16px;}
  [data-testid="stMetricLabel"] p {font-size: 0.85rem; color: #5B6577;}
  .tag {display:inline-block; padding:2px 10px; border-radius:999px; font-weight:600; font-size:0.85rem; color:white;}
  .SAFE {background:#2E7D5B;} .BORDERLINE {background:#E8A33D;} .SHORTAGE {background:#D64545;}
  .strip {display:flex; flex-wrap:wrap; gap:3px; margin:6px 0 4px;}
  .strip span {width:14px; height:14px; border-radius:3px; display:inline-block;}
  .P {background:#2E7D5B;} .A {background:#D64545;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data (read fresh on every page load)
settings = fe.load_settings()
students = fe.load_students()
register = fe.load_attendance()
lookup = ds.build_lookup(students)


def label(usn):
    return f"{ds.roll_of(usn)} · {lookup[usn]}"


def records():
    return [(usn, name, *ds.student_counts(register, usn)) for usn, name in students]


def dataframe():
    return analysis.load_dataframe() if register else None


def show(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


app = SimpleNamespace(settings=settings, students=students, register=register,
                      threshold=settings["threshold"], lookup=lookup,
                      label=label, records=records, dataframe=dataframe, show=show)


# ---------------------------------------------------------------- sidebar
st.sidebar.title("PresentSir")
st.sidebar.caption("Smart Attendance Tracker · Group 05")
role = st.sidebar.radio("I am a", ["Teacher", "Student"], horizontal=True)

TEACHER_PAGES = {
    "Dashboard": overview.render_dashboard,
    "Mark attendance": attendance_entry.render_mark,
    "Edit a record": attendance_entry.render_edit,
    "Student lookup": lookup_shortage.render_lookup,
    "Shortage list": lookup_shortage.render_shortage,
    "Class register": register_manage.render_register,
    "Analysis report": overview.render_analysis,
    "Manage class": register_manage.render_manage,
}

if role == "Student":
    render = student_portal.render_portal
else:
    page = st.sidebar.radio("Go to", list(TEACHER_PAGES), label_visibility="collapsed")
    render = TEACHER_PAGES[page]

st.sidebar.divider()
st.sidebar.markdown(f"**{settings['class_name']}**")
st.sidebar.markdown(f"{len(students)} students · {len(register)} class days")
st.sidebar.markdown(f"Required attendance: **{settings['threshold']}%**")

if not students:
    st.warning("No students found. Run `python generate_data.py` for sample data, "
               "or add students in **Manage class**.")

render(app)
