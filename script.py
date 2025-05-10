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


print("\n--------CERINTA 1--------")

# Calcularea mediei scorurilor la examene pentru fiecare grup
avg_scores = {}
for group in df["study_group"].dropna().unique():
    avg_scores[group] = df[df["study_group"] == group]["exam_score"].mean()

print("Media scorurilor la examene pentru fiecare interval de ore de studiu:")
for group, score in avg_scores.items():
    print(f"Grupa {group} ore: {score:.2f}")

# Identificarea studenților cu cel mai mare scor pentru fiecare interval de studiu
top_students = []
for group in df["study_group"].dropna().unique():
    group_df = df[df["study_group"] == group]
    if not group_df.empty:
        top_student = group_df.loc[group_df["exam_score"].idxmax()]
        top_students.append(
            (group, top_student["student_id"], top_student["exam_score"])
        )

print("\nStudenții cu cel mai mare scor pentru fiecare interval de studiu:")
for group, student_id, score in top_students:
    print(f"Grupa {group} ore: Studentul {student_id} cu scorul {score:.2f}")

# CERINTA 2
print("\n--------CERINTA 2--------")
# Crearea unui tuplu cu top 10 studenți în funcție de scorul la examen
top_performers = tuple(
    df.nlargest(10, "exam_score")[
        ["student_id", "exam_score", "social_media_hours"]
    ].itertuples(index=False, name="Student")
)

print("Top 10 studenți cu cele mai mari scoruri și timpul petrecut pe rețele sociale:")
for student in top_performers:
    print(
        f"Student ID: {student[0]}, Scor examen: {student[1]:.2f}, Ore pe rețele sociale: {student[2]:.2f}"
    )

# Identificarea nivelurilor de sănătate mintală pentru studenții cu performanțe ridicate (peste 90)
high_performers = df[df["exam_score"] > 90]
mental_health_levels = set(high_performers["mental_health_rating"])

print("\nNivelurile de sănătate mintală pentru studenții cu scoruri peste 90:")
print(mental_health_levels)

# Calcularea mediei de ore de studiu pentru fiecare nivel de sănătate mintală
mental_health_study_avg = {}
for level in mental_health_levels:
    avg = df[df["mental_health_rating"] == level]["study_hours_per_day"].mean()
    mental_health_study_avg[level] = avg

print("\nMedia orelor de studiu pentru fiecare nivel de sănătate mintală:")
for level, avg in sorted(mental_health_study_avg.items()):
    print(f"Nivel sănătate mintală: {level}, Media ore studiu: {avg:.2f}")


print("\n--------CERINTA 3--------")
