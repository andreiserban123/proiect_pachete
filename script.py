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


def analyze_sleep_vs_performance(data, bins=5):
    """
    Analizează relația dintre orele de somn și performanța la examene

    Args:
        data (DataFrame): Setul de date cu informații despre studenți
        bins (int): Numărul de intervale pentru gruparea orelor de somn

    Returns:
        dict: Dicționar cu mediile scorurilor pentru fiecare interval de somn
    """
    data["sleep_group"] = pd.cut(data["sleep_hours"], bins=bins)
    sleep_vs_score = data.groupby("sleep_group")["exam_score"].mean()
    return sleep_vs_score


def plot_sleep_vs_performance(sleep_vs_score):
    """
    Creează un grafic pentru relația dintre orele de somn și performanța la examene

    Args:
        sleep_vs_score (Series): Mediile scorurilor pentru fiecare interval de somn
    """
    plt.figure(figsize=(10, 6))
    sleep_vs_score.plot(kind="bar", color="skyblue")
    plt.title("Influența orelor de somn asupra performanței academice")
    plt.xlabel("Ore de somn")
    plt.ylabel("Scor mediu la examene")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    return plt


# Apelarea funcțiilor
sleep_vs_score = analyze_sleep_vs_performance(df)
print("Media scorurilor la examene pentru fiecare interval de ore de somn:")
print(sleep_vs_score)

# Crearea graficului
plt_sleep = plot_sleep_vs_performance(sleep_vs_score)


# Analiza suplimentară: comparație între studenții cu somn adecvat (7-9 ore) și cei cu somn insuficient (<6 ore)
def compare_sleep_groups(data):
    """
    Compară performanța studenților cu somn adecvat și insuficient

    Args:
        data (DataFrame): Setul de date cu informații despre studenți

    Returns:
        tuple: Mediile scorurilor pentru studenții cu somn adecvat și insuficient
    """
    adequate_sleep = data[(data["sleep_hours"] >= 7) & (data["sleep_hours"] <= 9)][
        "exam_score"
    ].mean()
    insufficient_sleep = data[data["sleep_hours"] < 6]["exam_score"].mean()
    return adequate_sleep, insufficient_sleep


adequate_sleep_score, insufficient_sleep_score = compare_sleep_groups(df)
print(
    f"\nMedia scorurilor pentru studenții cu somn adecvat (7-9 ore): {adequate_sleep_score:.2f}"
)
print(
    f"Media scorurilor pentru studenții cu somn insuficient (<6 ore): {insufficient_sleep_score:.2f}"
)
print(f"Diferența: {adequate_sleep_score - insufficient_sleep_score:.2f} puncte")

# Reprezentarea grafică a comparației
plt.figure(figsize=(8, 6))
plt.bar(
    ["Somn insuficient (<6 ore)", "Somn adecvat (7-9 ore)"],
    [insufficient_sleep_score, adequate_sleep_score],
    color=["salmon", "mediumseagreen"],
)
plt.title("Comparație între studenții cu somn adecvat și insuficient")
plt.ylabel("Scor mediu la examene")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
# plt.show()


print("\n--------CERINTA 4--------")

# Accesarea datelor cu loc - studenții care au un job part-time și scoruri peste 85
high_performing_workers = df.loc[
    (df["part_time_job"] == "Yes") & (df["exam_score"] > 85),
    ["student_id", "study_hours_per_day", "sleep_hours", "exam_score"],
]

print("Studenții cu job part-time și scoruri peste 85:")
print(high_performing_workers.head())


# Funcție pentru extragerea datelor cu iloc
def extract_student_data(data, row_indices):
    """
    Extrage date despre studenți folosind iloc

    Args:
        data (DataFrame): Setul de date cu informații despre studenți
        row_indices (list): Lista cu indici de rânduri pentru extragere

    Returns:
        DataFrame: Datele extrase pentru studenții specificați
    """
    selected_students = data.iloc[
        row_indices
    ]  # Extrage coloanele student_id, study_hours, attendance, sleep_hours, exam_score
    return selected_students


# Extragerea datelor pentru primii 5 studenți cu cele mai mari scoruri
top_5_indices = df["exam_score"].nlargest(5).index
top_5_students = extract_student_data(df, top_5_indices)

print("\nTop 5 studenți cu cele mai mari scoruri și obiceiurile lor:")
print(top_5_students)

# Analiza statistică pentru studenții cu job part-time vs. fără job
with_job = df[df["part_time_job"] == "Yes"]["exam_score"].describe()
without_job = df[df["part_time_job"] == "No"]["exam_score"].describe()

print("\nStatistici pentru studenții cu job part-time:")
print(with_job)
print("\nStatistici pentru studenții fără job part-time:")
print(without_job)

print("\n--------CERINTA 5--------")
# Gruparea datelor după calitatea dietei și calcularea statisticilor pentru scorurile la examene
diet_performance = df.groupby("diet_quality")["exam_score"].agg(
    ["mean", "median", "std", "count"]
)
print("Relația dintre calitatea dietei și performanța academică:")
print(diet_performance)

# Gruparea datelor după frecvența exercițiilor și calcularea statisticilor pentru scorurile la examene
exercise_performance = df.groupby("exercise_frequency")["exam_score"].agg(
    ["mean", "median", "std", "count"]
)
print("\nRelația dintre frecvența exercițiilor și performanța academică:")
print(exercise_performance)

# Analiza combinată a efectului dietei și exercițiilor asupra performanței
diet_exercise_performance = (
    df.groupby(["diet_quality", "exercise_frequency"])["exam_score"].mean().unstack()
)
print("\nMedia scorurilor la examene în funcție de dietă și exerciții:")
print(diet_exercise_performance)

# Analiza corelației dintre variabilele numerice
correlation_matrix = df[
    [
        "age",
        "study_hours_per_day",
        "social_media_hours",
        "netflix_hours",
        "attendance_percentage",
        "sleep_hours",
        "exercise_frequency",
        "mental_health_rating",
        "exam_score",
    ]
].corr()

print("\nMatricea de corelație pentru variabilele numerice:")
print(correlation_matrix["exam_score"].sort_values(ascending=False))

# Identificarea factorilor cu cel mai mare impact pozitiv și negativ asupra performanței
positive_factors = correlation_matrix["exam_score"].sort_values(ascending=False)
negative_factors = correlation_matrix["exam_score"].sort_values()

print("\nFactori cu impact pozitiv (corelații pozitive cu scorul la examene):")
for factor, corr in positive_factors.items():
    if factor != "exam_score" and corr > 0:
        print(f"{factor}: {corr:.4f}")

print("\nFactori cu impact negativ (corelații negative cu scorul la examene):")
for factor, corr in negative_factors.items():
    if factor != "exam_score" and corr < 0:
        print(f"{factor}: {corr:.4f}")
