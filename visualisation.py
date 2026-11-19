"""
Component 6 - Visualisation and report
Owner: Venkata Krishnan.S (25BTLDC001)

Four labelled matplotlib charts, saved as PNG files in charts/:
  1. attendance_percentage_bar.png  - every student's %, shortage bars in red
  2. daily_present_line.png         - present count per day with 5-day average
  3. shortage_highlight.png         - students below 75% and classes they need
  4. dashboard_subplots.png         - 2x2 subplots: weekday, distribution, status, month
"""

import os

import matplotlib
matplotlib.use("Agg")  # save files without needing a display window
import matplotlib.pyplot as plt
import matplotlib.ticker

import analysis

CHART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")

SAFE = "#2E7D5B"
SHORT = "#D64545"
BORDER = "#E8A33D"
INK = "#1F2A44"
GRID = "#E3E6EC"

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.edgecolor": "#B9BFCA",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "axes.axisbelow": True,
})


def _save(fig, filename, save=True):
    """Save the figure as a PNG and return the path; with save=False return the figure (used by app.py)."""
    if not save:
        return fig
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def attendance_bar(df, threshold=75, save=True):
    sw = analysis.student_wise(df, threshold)
    colors = [SHORT if p < threshold else BORDER if p < threshold + 10 else SAFE for p in sw["percentage"]]
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.bar(sw["usn"].str[-3:], sw["percentage"], color=colors, width=0.75)
    ax.axhline(threshold, color=INK, linestyle="--", linewidth=1.2)
    ax.set_title("Attendance % of every student (sorted lowest to highest)")
    ax.set_xlabel("Roll number (last 3 digits of USN)")
    ax.set_ylabel("Attendance %")
    ax.set_ylim(0, 105)
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)
    ax.grid(axis="x", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (SHORT, BORDER, SAFE)]
    handles.append(plt.Line2D([0], [0], color=INK, linestyle="--"))
    ax.legend(handles, [f"Shortage (<{threshold}%)", f"Borderline ({threshold}-{threshold + 10}%)",
                        f"Safe (>={threshold + 10}%)", f"Required {threshold}%"],
              loc="upper left", frameon=True, facecolor="white", edgecolor="white", framealpha=1)
    return _save(fig, "attendance_percentage_bar.png", save)


def daily_line(df, save=True):
    dw = analysis.date_wise(df)
    strength = int(dw["strength"].max())
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(dw["date"], dw["present"], marker="o", markersize=3.5, linewidth=1.2,
            color="#4A6FA5", label="Students present")
    ax.plot(dw["date"], dw["rolling_5day"], linewidth=2.5, color=INK, label="5-day rolling average")
    ax.axhline(strength * 0.75, color=SHORT, linestyle="--", linewidth=1, label="75% of class strength")
    low = dw.loc[dw["present"].idxmin()]
    ax.annotate(f"Lowest: {low['present']} on {low['date']:%d %b}", xy=(low["date"], low["present"]),
                xytext=(10, -22), textcoords="offset points", fontsize=9, color=SHORT,
                arrowprops=dict(arrowstyle="->", color=SHORT))
    ax.set_title("Daily present count across the semester")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Students present (out of {strength})")
    ax.set_ylim(0, strength + 3)
    ax.legend(loc="lower left", frameon=False, ncol=3)
    fig.autofmt_xdate()
    return _save(fig, "daily_present_line.png", save)


def shortage_highlight(df, threshold=75, save=True):
    short = analysis.shortage_list(df, threshold).sort_values("percentage", ascending=False)
    fig, ax = plt.subplots(figsize=(11, max(3.5, 0.45 * len(short) + 1.5)))
    if short.empty:
        ax.text(0.5, 0.5, "No students below the threshold", ha="center", va="center", fontsize=14)
        ax.axis("off")
    else:
        labels = short["name"] + "  (" + short["usn"].str[-3:] + ")"
        ax.barh(labels, [100] * len(short), color=GRID, height=0.6)
        bars = ax.barh(labels, short["percentage"], color=SHORT, height=0.6)
        ax.axvline(threshold, color=INK, linestyle="--", linewidth=1.2)
        for bar, pct, need in zip(bars, short["percentage"], short["classes_needed"]):
            ax.text(bar.get_width() - 1, bar.get_y() + bar.get_height() / 2, f"{pct:.1f}%",
                    va="center", ha="right", color="white", fontsize=9, fontweight="bold")
            ax.text(101, bar.get_y() + bar.get_height() / 2, f"needs {need} more class{'' if need == 1 else 'es'}",
                    va="center", fontsize=9, color=INK)
        ax.set_xlim(0, 125)
        ax.set_xlabel("Attendance %")
        ax.grid(axis="y", visible=False)
    ax.set_title(f"Shortage alert: {len(short)} students below {threshold}% and the classes each needs to recover")
    return _save(fig, "shortage_highlight.png", save)


def dashboard(df, threshold=75, save=True):
    sw = analysis.student_wise(df, threshold)
    wk = analysis.weekday_pattern(df)
    mo = analysis.monthly_pattern(df)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("PresentSir attendance dashboard", fontsize=16, fontweight="bold", color=INK)

    ax = axes[0, 0]
    bars = ax.bar(wk.index.str[:3], wk.values, color=[SHORT if v == wk.min() else "#4A6FA5" for v in wk.values])
    ax.bar_label(bars, fmt="%.1f%%", fontsize=9)
    ax.set_title("Average attendance by weekday")
    ax.set_ylabel("Attendance %")
    ax.set_ylim(min(wk.min() - 10, threshold - 5), 100)

    ax = axes[0, 1]
    ax.hist(sw["percentage"], bins=range(40, 105, 5), color="#4A6FA5", edgecolor="white")
    ax.axvline(threshold, color=SHORT, linestyle="--", label=f"{threshold}% line")
    ax.set_title("How attendance % is spread across the class")
    ax.set_xlabel("Attendance %")
    ax.set_ylabel("Number of students")
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.legend(frameon=False)

    ax = axes[1, 0]
    counts = [(sw["percentage"] >= threshold + 10).sum(),
              ((sw["percentage"] >= threshold) & (sw["percentage"] < threshold + 10)).sum(),
              (sw["percentage"] < threshold).sum()]
    ax.pie(counts, labels=["Safe", "Borderline", "Shortage"], colors=[SAFE, BORDER, SHORT],
           autopct=lambda p: f"{p:.0f}%\n({round(p * sum(counts) / 100)})", startangle=90,
           wedgeprops=dict(width=0.45, edgecolor="white"), textprops=dict(fontsize=10))
    ax.set_title("Students by attendance status")

    ax = axes[1, 1]
    bars = ax.bar(mo.index, mo.values, color="#4A6FA5")
    ax.bar_label(bars, fmt="%.1f%%", fontsize=9)
    ax.axhline(threshold, color=SHORT, linestyle="--")
    ax.set_title("Average attendance by month")
    ax.set_ylabel("Attendance %")
    ax.set_ylim(min(mo.min() - 10, threshold - 5), 100)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, "dashboard_subplots.png", save)


def student_report(df, usn, threshold=75, save=True):
    """Three charts for one student: running % over time, month by month, weekday by weekday."""
    tl = analysis.student_timeline(df, usn)
    mo = analysis.student_monthly(df, usn)
    wk = analysis.student_weekday(df, usn)
    name = df.loc[df["usn"] == usn, "name"].iloc[0]

    fig = plt.figure(figsize=(13, 8))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.1, 1])
    fig.suptitle(f"{name} ({usn}): attendance report", fontsize=15, fontweight="bold", color=INK)

    ax = fig.add_subplot(grid[0, :])
    ax.plot(tl["date"], tl["running_pct"], color="#4A6FA5", linewidth=2.2, label="Running attendance %")
    absent = tl[tl["present"] == 0]
    ax.scatter(absent["date"], absent["running_pct"], color=SHORT, s=22, zorder=3, label="Absent that day")
    ax.axhline(threshold, color=INK, linestyle="--", linewidth=1, label=f"Required {threshold}%")
    ax.set_title("Attendance % after every class")
    ax.set_ylabel("Attendance %")
    ax.set_ylim(max(0, min(tl["running_pct"].min(), threshold) - 10), 101)
    ax.legend(loc="lower left", frameon=False, ncol=3)

    ax = fig.add_subplot(grid[1, 0])
    bars = ax.bar(mo["month"], mo["percentage"],
                  color=[SHORT if p < threshold else SAFE for p in mo["percentage"]])
    ax.bar_label(bars, labels=[f"{p:.0f}%\n({a}/{t})" for p, a, t in
                               zip(mo["percentage"], mo["attended"], mo["total"])], fontsize=9)
    ax.axhline(threshold, color=INK, linestyle="--", linewidth=1)
    ax.set_title("Month by month")
    ax.set_ylabel("Attendance %")
    ax.set_ylim(0, 118)

    ax = fig.add_subplot(grid[1, 1])
    bars = ax.bar(wk.index.str[:3], wk.values,
                  color=[SHORT if v < threshold else "#4A6FA5" for v in wk.values])
    ax.bar_label(bars, fmt="%.0f%%", fontsize=9)
    ax.axhline(threshold, color=INK, linestyle="--", linewidth=1)
    ax.set_title("By day of the week")
    ax.set_ylim(0, 110)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, f"student_{usn}.png", save)


def generate_all(df, threshold=75):
    return [
        attendance_bar(df, threshold),
        daily_line(df),
        shortage_highlight(df, threshold),
        dashboard(df, threshold),
    ]
