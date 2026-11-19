"""
Component 5 - Data analysis (pandas + NumPy)
Owner: Vishal Tejas (25BTRDC055)

Reads attendance.csv and students.csv into DataFrames and answers:
  * student-wise attendance %   * date-wise present count
  * shortage list               * weekday and monthly patterns
"""

import numpy as np
import pandas as pd

from files_errors import ATTENDANCE_FILE, STUDENTS_FILE

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def load_dataframe(attendance_path=ATTENDANCE_FILE, students_path=STUDENTS_FILE):
    """Merge attendance with the student list and add helper columns."""
    att = pd.read_csv(attendance_path)
    students = pd.read_csv(students_path)

    att = att.dropna(subset=["date", "usn"])               # rows without a date/USN are useless
    att["status"] = att["status"].fillna("A").str.upper()  # a missing status counts as absent
    att["date"] = pd.to_datetime(att["date"], errors="coerce")
    att = att.dropna(subset=["date"])

    df = att.drop(columns=["name"], errors="ignore").merge(students, on="usn", how="left")
    df["name"] = df["name"].fillna("Unknown")
    df["present"] = np.where(df["status"] == "P", 1, 0)
    df["weekday"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.strftime("%b %Y")
    return df


def student_wise(df, threshold=75):
    out = (df.groupby(["usn", "name"])["present"]
             .agg(attended="sum", total="count")
             .reset_index())
    out["percentage"] = (out["attended"] / out["total"] * 100).round(2)
    out["shortage"] = out["percentage"] < threshold
    return out.sort_values("percentage").reset_index(drop=True)


def date_wise(df):
    out = (df.groupby("date")["present"]
             .agg(present="sum", strength="count")
             .reset_index())
    out["percentage"] = (out["present"] / out["strength"] * 100).round(2)
    out["rolling_5day"] = out["present"].rolling(5, min_periods=1).mean().round(1)
    return out


def shortage_list(df, threshold=75):
    """Students below threshold with classes needed, computed on NumPy arrays."""
    sw = student_wise(df, threshold)
    short = sw[sw["shortage"]].copy()
    a = short["attended"].to_numpy()
    t = short["total"].to_numpy()
    r = threshold / 100
    short["classes_needed"] = np.ceil((r * t - a) / (1 - r) - 1e-9).clip(min=0).astype(int)
    return short.sort_values("classes_needed", ascending=False).reset_index(drop=True)


def weekday_pattern(df):
    out = df.groupby("weekday")["present"].mean().mul(100).round(2)
    return out.reindex([d for d in WEEKDAY_ORDER if d in out.index])


def monthly_pattern(df):
    out = df.groupby(df["date"].dt.to_period("M"))["present"].mean().mul(100).round(2)
    out.index = out.index.strftime("%b %Y")
    return out


def student_timeline(df, usn):
    """One student's attendance day by day, with the running percentage after each class."""
    one = df[df["usn"] == usn].sort_values("date").copy()
    one["attended_so_far"] = one["present"].cumsum()
    one["classes_so_far"] = np.arange(1, len(one) + 1)
    one["running_pct"] = (one["attended_so_far"] / one["classes_so_far"] * 100).round(2)
    return one[["date", "weekday", "month", "status", "present", "attended_so_far", "classes_so_far", "running_pct"]]


def student_monthly(df, usn):
    one = df[df["usn"] == usn]
    out = (one.groupby(one["date"].dt.to_period("M"))["present"]
              .agg(attended="sum", total="count").reset_index())
    out["percentage"] = (out["attended"] / out["total"] * 100).round(2)
    out["month"] = out["date"].dt.strftime("%b %Y")
    return out[["month", "attended", "total", "percentage"]]


def student_weekday(df, usn):
    one = df[df["usn"] == usn]
    out = one.groupby("weekday")["present"].mean().mul(100).round(2)
    return out.reindex([d for d in WEEKDAY_ORDER if d in out.index])


def register_matrix(df):
    """Student x date grid of 1/0. Students added mid-term get 0 (fillna) for earlier days."""
    grid = df.pivot_table(index="name", columns="date", values="present", aggfunc="sum")
    grid = grid.sort_index(axis=1)                      # real date order, not alphabetical
    grid.columns = grid.columns.strftime("%d-%b")
    return grid.fillna(0).astype(int)


def overall_stats(df, threshold=75):
    sw = student_wise(df, threshold)
    pct = sw["percentage"].to_numpy()
    return {
        "students": len(sw),
        "class_days": df["date"].nunique(),
        "records": len(df),
        "class_average": round(float(np.mean(pct)), 2),
        "median": round(float(np.median(pct)), 2),
        "highest": round(float(np.max(pct)), 2),
        "lowest": round(float(np.min(pct)), 2),
        "std_dev": round(float(np.std(pct)), 2),
        "shortage_count": int((pct < threshold).sum()),
    }


def full_report(df, threshold=75):
    """Combine the top 5 and bottom 5 students into one table with concat."""
    sw = student_wise(df, threshold)
    top = sw.tail(5).iloc[::-1].assign(group="Top 5")
    bottom = sw.head(5).assign(group="Bottom 5")
    return pd.concat([top, bottom], ignore_index=True)


def print_report(df, threshold=75):
    stats = overall_stats(df, threshold)
    print("\n========== PresentSir : ANALYSIS REPORT ==========")
    print(f"Records analysed : {stats['records']}  ({stats['students']} students x {stats['class_days']} class days)")
    print(f"Class average    : {stats['class_average']}%   (median {stats['median']}%, std dev {stats['std_dev']})")
    print(f"Highest / lowest : {stats['highest']}% / {stats['lowest']}%")
    print(f"Below {threshold}%        : {stats['shortage_count']} students")

    print("\n-- Top 5 and bottom 5 students --")
    print(full_report(df, threshold)[["group", "usn", "name", "attended", "total", "percentage"]]
          .to_string(index=False))

    print("\n-- Shortage list (most classes needed first) --")
    short = shortage_list(df, threshold)
    if short.empty:
        print("No students below the threshold.")
    else:
        print(short[["usn", "name", "attended", "total", "percentage", "classes_needed"]]
              .to_string(index=False))

    print("\n-- Average attendance by weekday --")
    for day, pct in weekday_pattern(df).items():
        print(f"  {day:<10} {pct:6.2f}%  {'#' * int(pct // 4)}")

    print("\n-- Average attendance by month --")
    for month, pct in monthly_pattern(df).items():
        print(f"  {month:<10} {pct:6.2f}%")

    dw = date_wise(df)
    low = dw.sort_values("present").head(3)
    print("\n-- Lowest-turnout days --")
    for _, row in low.iterrows():
        print(f"  {row['date']:%a %d-%b-%Y}  {row['present']}/{row['strength']} present ({row['percentage']}%)")
    print("=" * 50)
