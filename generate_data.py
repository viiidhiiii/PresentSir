"""
Creates realistic sample data with the random module:
  60 students x every working day from 3 Aug to 13 Nov 2026 (minus holidays).

Each student gets their own attendance habit, Mondays and Fridays are a
little weaker, and the week before mid-terms is stronger, so the charts
have real patterns to find.

Owner: Vishal Tejas (25BTRDC055)

Run once:   python generate_data.py
"""

import random
from datetime import date, timedelta

import data_structures as ds
import files_errors as fe

random.seed(5)  # group 05 - same data every time

FIRST = ["Aarav", "Ananya", "Rohan", "Diya", "Kabir", "Ishita", "Vivaan", "Meera", "Arjun", "Sneha",
         "Aditya", "Kavya", "Reyansh", "Pooja", "Siddharth", "Nisha", "Varun", "Tanvi", "Karthik", "Riya",
         "Harsh", "Shruti", "Nikhil", "Aditi", "Pranav", "Sana", "Yash", "Lakshmi", "Manav", "Divya",
         "Rahul", "Neha", "Akash", "Priya", "Dhruv", "Swathi", "Kunal", "Bhavna", "Tejas", "Fatima",
         "Gautam", "Anjali", "Rishi", "Keerthi", "Omkar", "Simran", "Sameer", "Deepika", "Ashwin", "Pallavi",
         "Chirag", "Nandini", "Irfan", "Rachana", "Mohit", "Varsha", "Sahil", "Harini", "Abhishek", "Megha"]
LAST = ["Sharma", "Reddy", "Iyer", "Nair", "Gowda", "Patel", "Rao", "Menon", "Kulkarni", "Shetty",
        "Hegde", "Joshi", "Verma", "Pillai", "Bhat", "Kapoor", "Naidu", "Desai", "Khan", "Kumar"]

HOLIDAYS = {date(2026, 8, 15), date(2026, 8, 27), date(2026, 10, 2), date(2026, 10, 20), date(2026, 10, 21)}
WEEKDAY_EFFECT = {0: -0.06, 1: 0.01, 2: 0.03, 3: 0.01, 4: -0.08}  # Mon .. Fri


def class_days(start=date(2026, 8, 3), end=date(2026, 11, 13)):
    d, days = start, []
    while d <= end:
        if d.weekday() < 5 and d not in HOLIDAYS:
            days.append(d)
        d += timedelta(days=1)
    return days


def main():
    students = [(f"{ds.USN_PREFIX}{i:03d}", f"{FIRST[i - 1]} {random.choice(LAST)}") for i in range(1, 61)]

    # personal habit: most students attend 80-97%, a group of ~12 is at risk
    habit = {}
    for usn, _ in students:
        habit[usn] = random.uniform(0.55, 0.76) if random.random() < 0.2 else random.uniform(0.80, 0.97)

    register = {}
    for d in class_days():
        boost = 0.05 if date(2026, 9, 21) <= d <= date(2026, 9, 25) else 0.0  # pre mid-term week
        register[d.isoformat()] = {
            usn for usn, _ in students
            if random.random() < min(0.99, habit[usn] + WEEKDAY_EFFECT[d.weekday()] + boost)
        }

    fe.save_students(students)
    rows = fe.save_attendance(register, students)
    fe.save_settings(fe.DEFAULT_SETTINGS)
    print(f"Created {len(students)} students, {len(register)} class days, {rows} attendance rows.")


if __name__ == "__main__":
    main()
