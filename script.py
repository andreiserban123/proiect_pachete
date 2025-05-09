import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Citirea setului de date
df = pd.read_csv("student_habits_performance.csv")

# Gruparea orelor de studiu în intervale
df["study_group"] = pd.cut(
    df["study_hours_per_day"],
    bins=[0, 2, 4, 6, 8, 10],
    labels=["0-2", "2-4", "4-6", "6-8", "8-10"],
)

# Calcularea mediei scorurilor la examene pentru fiecare grup
avg_scores = {}
for group in df["study_group"].unique():
    avg_scores[group] = df[df["study_group"] == group]["exam_score"].mean()

print("Media scorurilor la examene pentru fiecare interval de ore de studiu:")
for group, score in avg_scores.items():
    print(f"Grupa {group} ore: {score:.2f}")

# Identificarea studenților cu cel mai mare scor pentru fiecare interval de studiu
top_students = []
for group in df["study_group"].unique():
    group_df = df[df["study_group"] == group]
    top_student = group_df.loc[group_df["exam_score"].idxmax()]
    top_students.append((group, top_student["student_id"], top_student["exam_score"]))

print("\nStudenții cu cel mai mare scor pentru fiecare interval de studiu:")
for group, student_id, score in top_students:
    print(f"Grupa {group} ore: Studentul {student_id} cu scorul {score:.2f}")
