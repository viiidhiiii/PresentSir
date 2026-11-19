"""
PresentSir website (ADDITIONAL work, beyond the brief)
Student login and the student's personal attendance view.
Owner: Kaushik M R (25BTRDC028)

Each render_*() function draws one page. `app` carries the data loaded in website/app.py.
"""

import streamlit as st

import analysis
import core_logic as core
import data_structures as ds
import visualisation as viz


def render_portal(app):
    """Student portal page."""
    register, threshold, lookup = app.register, app.threshold, app.lookup
    dataframe, show = app.dataframe, app.show

    me = st.session_state.get("student")

    if not me:
        st.title("Student login")
        st.caption("Log in to see your own attendance.")
        with st.form("login"):
            usn_in = st.text_input("USN", placeholder="e.g. 25DEMO054").strip().upper()
            name_in = st.text_input("Full name, as on the class list")
            if st.form_submit_button("Log in", type="primary"):
                if usn_in not in lookup:
                    st.error("That USN is not on the class list.")
                elif " ".join(name_in.lower().split()) != lookup[usn_in].lower():
                    st.error("The name doesn't match this USN.")
                else:
                    st.session_state["student"] = usn_in
                    st.rerun()
        st.caption("Demo login: USN **25DEMO054**, name **Rachana Iyer**.")
        st.stop()

    attended, total = ds.student_counts(register, me)
    pct = core.attendance_percentage(attended, total)
    status = core.status_label(pct, threshold)

    top, out = st.columns([5, 1])
    top.markdown(f"## Hi, {lookup[me].split()[0]} 👋")
    if out.button("Log out"):
        del st.session_state["student"]
        st.rerun()
    st.markdown(f"{lookup[me]} · {me} &nbsp; <span class='tag {status}'>{status}</span>", unsafe_allow_html=True)

    if total == 0:
        st.info("No classes recorded yet.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("My attendance", f"{pct}%")
    c2.metric("Classes attended", f"{attended} / {total}")
    c3.metric("Classes missed", total - attended)
    if core.is_shortage(pct, threshold):
        need = core.classes_needed(attended, total, threshold)
        c4.metric("Classes needed", need)
        st.error(f"You are below {threshold}%. Attend the next {core.classes_text(need)} "
                 f"in a row to get back to {threshold}%.")
    else:
        skip = core.classes_can_skip(attended, total, threshold)
        c4.metric("Classes you can miss", skip)
        st.success(f"You're above {threshold}%. You can miss {core.classes_text(skip)} "
                   f"and still stay at or above {threshold}%.")

    df = dataframe()
    show(viz.student_report(df, me, threshold, save=False))

    tl = analysis.student_timeline(df, me)
    left, right = st.columns(2)
    with left:
        st.subheader("Month by month")
        st.dataframe(analysis.student_monthly(df, me), hide_index=True, width="stretch",
                     column_config={"month": "Month", "attended": "Attended", "total": "Classes",
                                    "percentage": st.column_config.ProgressColumn(
                                        "Attendance", format="%.1f%%", min_value=0, max_value=100)})
        class_avg = analysis.overall_stats(df, threshold)["class_average"]
        st.caption(f"Class average: {class_avg}%. You are "
                   f"{abs(pct - class_avg):.1f} points {'above' if pct >= class_avg else 'below'} it.")
    with right:
        st.subheader("Every class")
        only_absent = st.toggle("Show only the days I was absent")
        rows = tl[tl["present"] == 0] if only_absent else tl
        st.dataframe(
            rows.assign(date=rows["date"].dt.strftime("%Y-%m-%d"),
                        status=rows["status"].map({"P": "Present", "A": "Absent"}))
                [["date", "weekday", "status", "running_pct"]].iloc[::-1],
            hide_index=True, width="stretch", height=320,
            column_config={"date": "Date", "weekday": "Day", "status": "Status",
                           "running_pct": st.column_config.NumberColumn("My % after this class",
                                                                        format="%.1f%%")})
