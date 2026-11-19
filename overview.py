"""
PresentSir website (ADDITIONAL work, beyond the brief)
Dashboard and Analysis report pages.
Owner: Vishal Tejas (25BTRDC055)

Each render_*() function draws one page. `app` carries the data loaded in website/app.py.
"""

import streamlit as st

import analysis
import data_structures as ds
import visualisation as viz


def render_dashboard(app):
    """Dashboard page."""
    students, register, threshold = app.students, app.register, app.threshold
    dataframe, show = app.dataframe, app.show

    st.title("Attendance dashboard")
    if not register:
        st.info("No attendance recorded yet. Start with **Mark attendance**.")
        st.stop()

    df = dataframe()
    stats = analysis.overall_stats(df, threshold)
    days = sorted(register)
    today_count = len(register[days[-1]])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", stats["students"])
    c2.metric("Class days recorded", stats["class_days"], help=f"{days[0]} to {days[-1]}")
    c3.metric("Class average", f"{stats['class_average']}%")
    c4.metric(f"Below {threshold}%", stats["shortage_count"],
              help=f"{stats['shortage_count'] / stats['students'] * 100:.0f}% of the class")

    st.caption(f"Last class day: **{days[-1]}** ({ds.weekday_of(days[-1])}): "
               f"{today_count}/{len(students)} present")

    left, right = st.columns([3, 2])
    with left:
        show(viz.daily_line(df, save=False))
    with right:
        short = analysis.shortage_list(df, threshold)
        st.subheader("Needs attention")
        if short.empty:
            st.success(f"Everyone is at or above {threshold}%.")
        else:
            st.dataframe(
                short.assign(roll=short["usn"].str[-3:])[["roll", "name", "percentage", "classes_needed"]],
                hide_index=True, width="stretch",
                column_config={
                    "roll": "Roll", "name": "Name",
                    "percentage": st.column_config.ProgressColumn("Attendance", format="%.1f%%",
                                                                  min_value=0, max_value=100),
                    "classes_needed": st.column_config.NumberColumn("Classes needed"),
                })
    show(viz.attendance_bar(df, threshold, save=False))


def render_analysis(app):
    """Analysis report page."""
    register, threshold = app.register, app.threshold
    dataframe, show = app.dataframe, app.show

    st.title("Analysis report")
    if not register:
        st.info("No attendance recorded yet.")
        st.stop()
    df = dataframe()
    stats = analysis.overall_stats(df, threshold)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records analysed", f"{stats['records']:,}")
    c2.metric("Median attendance", f"{stats['median']}%")
    c3.metric("Highest", f"{stats['highest']}%")
    c4.metric("Lowest", f"{stats['lowest']}%", help=f"Standard deviation: {stats['std_dev']}")

    show(viz.dashboard(df, threshold, save=False))

    left, right = st.columns(2)
    with left:
        st.subheader("Top 5 and bottom 5")
        st.dataframe(analysis.full_report(df, threshold)[["group", "usn", "name", "percentage"]],
                     hide_index=True, width="stretch")
    with right:
        st.subheader("By weekday")
        st.dataframe(analysis.weekday_pattern(df).rename("Attendance %"), width="stretch")
        st.subheader("By month")
        st.dataframe(analysis.monthly_pattern(df).rename("Attendance %"), width="stretch")

    if st.button("Save all charts as PNG files"):
        for path in viz.generate_all(df, threshold):
            st.write(f"Saved `{path}`")
