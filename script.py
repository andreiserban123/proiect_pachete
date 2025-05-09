# Analiză Companie Retail - Implementarea tuturor cerințelor Python
# Scriptul utilizează fișierele CSV locale (vanzari.csv, produse.csv, filiale.csv, clienti.csv)

# Importul bibliotecilor necesare
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
import seaborn as sns
from datetime import datetime

print("=== ANALIZĂ COMPANIE RETAIL - PACHETE SOFTWARE ===\n")

print("\n*** 1. UTILIZAREA LISTELOR ȘI DICȚIONARELOR ***\n")

# Încărcăm datele despre produse
df_produse = pd.read_csv("produse.csv")

# Creăm o listă cu numele produselor
produse = df_produse["nume"].tolist()

# Creăm un dicționar pentru categoriile produselor
categorii_produse = dict(zip(df_produse["nume"], df_produse["categorie"]))

# Utilizăm metode specifice listelor
print("Lista produselor:")
print(produse)
print("\nPrimele 3 produse:", produse[:3])
produse.append("Smartwatch")  # Adăugăm un nou produs
print("\nLista actualizată:", produse)
produse.remove("Smartwatch")  # Ștergem produsul adăugat
print("\nLista după ștergere:", produse)

# Utilizăm metode specifice dicționarelor
print("\nCategoriile produselor:")
print(categorii_produse)
print("\nCheile dicționarului (produsele):", list(categorii_produse.keys()))
print("\nValorile dicționarului (categoriile):", list(categorii_produse.values()))
print("\nCategoria pentru Laptop:", categorii_produse.get("Laptop"))
print(
    "\nCategoria pentru un produs inexistent:",
    categorii_produse.get("Smartwatch", "Categorie nedefinită"),
)

# ----- 2. Utilizarea seturilor și a tuplurilor, incluzând metode specifice acestora -----
print("\n*** 2. UTILIZAREA SETURILOR ȘI TUPLURILOR ***\n")

# Creăm un set cu categoriile unice
categorii_unice = set(categorii_produse.values())
print("Categoriile unice:", categorii_unice)

# Adăugăm o categorie nouă în set
categorii_unice.add("Gadgeturi")
print("Set după adăugarea unei categorii:", categorii_unice)

# Ștergem o categorie din set
categorii_unice.remove("Gadgeturi")
print("Set după ștergerea unei categorii:", categorii_unice)

# Creăm tupluri pentru prețuri (preț achiziție, preț vânzare)
preturi_produse = {
    row["nume"]: (row["pret_achizitie"], row["pret_vanzare"])
    for _, row in df_produse.iterrows()
}

# Afișăm prețurile
print("\nPrețurile produselor (achiziție, vânzare):")
for produs, preturi in preturi_produse.items():
    print(f"{produs}: {preturi}")

# Calculăm marja de profit pentru fiecare produs folosind tupluri
marje_profit = {}
for produs, (pret_achizitie, pret_vanzare) in preturi_produse.items():
    marje_profit[produs] = round(
        (pret_vanzare - pret_achizitie) / pret_achizitie * 100, 2
    )

print("\nMarjele de profit pentru fiecare produs (%):")
for produs, marja in marje_profit.items():
    print(f"{produs}: {marja}%")

# ----- 3. Definirea și apelarea unor funcții -----
print("\n*** 3. DEFINIREA ȘI APELAREA UNOR FUNCȚII ***\n")


def calculeaza_profit(pret_achizitie, pret_vanzare, cantitate=1, discount=0):
    """
    Calculează profitul pentru un produs vândut.

    Args:
        pret_achizitie (float): Prețul de achiziție al produsului
        pret_vanzare (float): Prețul de vânzare al produsului
        cantitate (int): Numărul de unități vândute
        discount (float): Discount-ul aplicat ca procent (0-100)

    Returns:
        float: Profitul obținut după aplicarea discount-ului
    """
    pret_vanzare_dupa_discount = pret_vanzare * (1 - discount / 100)
    profit_per_unitate = pret_vanzare_dupa_discount - pret_achizitie
    return profit_per_unitate * cantitate


# Testăm funcția pentru diferite scenarii
print("Testarea funcției de calcul al profitului:")
print(f"Profit pentru 1 laptop fără discount: {calculeaza_profit(2500, 3500)} lei")
print(
    f"Profit pentru 2 televizoare cu discount de 10%: {calculeaza_profit(1800, 2500, 2, 10)} lei"
)
print(
    f"Profit pentru 3 telefoane cu discount de 20%: {calculeaza_profit(1200, 1800, 3, 20)} lei"
)


# Funcție pentru calculul performanței vânzărilor pe categorii
def analizeaza_performanta_pe_categorii(df_vanzari):
    """
    Analizează performanța vânzărilor pe categorii și returnează
    categoriile sortate după profit.

    Args:
        df_vanzari (DataFrame): DataFrame cu vânzările

    Returns:
        DataFrame: DataFrame cu categoriile sortate după profit
    """
    # Grupăm vânzările după categorie și calculăm profitul total
    performanta = (
        df_vanzari.groupby("categorie")
        .agg({"pret_total": "sum", "profit": "sum", "id": "count"})
        .reset_index()
    )

    # Redenumim coloanele
    performanta.columns = [
        "categorie",
        "vanzari_totale",
        "profit_total",
        "numar_tranzactii",
    ]

    # Calculăm marja de profit pentru fiecare categorie
    performanta["marja_profit"] = (
        performanta["profit_total"] / performanta["vanzari_totale"] * 100
    ).round(2)

    # Sortăm categoriile după profitul total în ordine descrescătoare
    performanta = performanta.sort_values(by="profit_total", ascending=False)

    return performanta


# Încărcăm datele despre vânzări
df_vanzari = pd.read_csv("vanzari.csv")

# Apelăm funcția
performanta_categorii = analizeaza_performanta_pe_categorii(df_vanzari)
print("\nPerformanța categoriilor de produse (ordine descrescătoare):")
print(performanta_categorii)

# ----- 4. Utilizarea structurilor condiționale -----
print("\n*** 4. UTILIZAREA STRUCTURILOR CONDIȚIONALE ***\n")


def evalueaza_performanta_produs(produs, vanzari, target):
    """
    Evaluează performanța unui produs pe baza vânzărilor și a targetului.

    Args:
        produs (str): Numele produsului
        vanzari (float): Valoarea vânzărilor
        target (float): Targetul de vânzări

    Returns:
        str: Evaluarea performanței
    """
    procent_realizare = (vanzari / target) * 100

    if procent_realizare >= 110:
        return f"{produs} - Performanță excelentă ({procent_realizare:.1f}% din target)"
    elif procent_realizare >= 95:
        return f"{produs} - Performanță bună ({procent_realizare:.1f}% din target)"
    elif procent_realizare >= 80:
        return f"{produs} - Performanță satisfăcătoare ({procent_realizare:.1f}% din target)"
    else:
        return f"{produs} - Performanță sub așteptări ({procent_realizare:.1f}% din target)"


# Calculăm vânzările totale pentru fiecare produs
vanzari_per_produs = df_vanzari.groupby("produs_nume")["pret_total"].sum()

# Definim targeturi bazate pe vânzări (pentru exemplificare)
target_produse = {}
for produs in vanzari_per_produs.index:
    # Targeturile sunt definite ca 90-110% din vânzările reale pentru demonstrație
    factor = np.random.uniform(0.9, 1.1)
    target_produse[produs] = vanzari_per_produs[produs] * factor

print("Evaluarea performanței produselor:")
for produs in vanzari_per_produs.index:
    print(
        evalueaza_performanta_produs(
            produs, vanzari_per_produs[produs], target_produse[produs]
        )
    )

# ----- 5. Utilizarea structurilor repetitive -----
print("\n*** 5. UTILIZAREA STRUCTURILOR REPETITIVE ***\n")

# Obținem lista lunilor unice din date și le sortăm cronologic
lunile_ordonate = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai"]
vanzari_lunare = df_vanzari.groupby("luna")["pret_total"].sum().reindex(lunile_ordonate)

print("Evoluția vânzărilor lunare (structură for):")
for i, luna in enumerate(lunile_ordonate):
    if luna in vanzari_lunare.index:
        print(f"{luna} 2023: {vanzari_lunare[luna]:.2f} lei")

# Calculăm creșterea procentuală față de luna anterioară folosind o structură while
print("\nCreșterea procentuală față de luna anterioară (structură while):")
i = 1
while i < len(lunile_ordonate):
    luna_curenta = lunile_ordonate[i]
    luna_anterioara = lunile_ordonate[i - 1]

    if luna_curenta in vanzari_lunare.index and luna_anterioara in vanzari_lunare.index:
        crestere = (
            (vanzari_lunare[luna_curenta] - vanzari_lunare[luna_anterioara])
            / vanzari_lunare[luna_anterioara]
        ) * 100
        print(f"{luna_curenta}: {crestere:.2f}%")
    i += 1

# Calculăm vânzări cumulative folosind o structură for
vanzari_cumulative = 0
print("\nVânzări cumulative (structură for):")
for luna in lunile_ordonate:
    if luna in vanzari_lunare.index:
        vanzari_cumulative += vanzari_lunare[luna]
        print(f"Până la sfârșitul lunii {luna}: {vanzari_cumulative:.2f} lei")

# ----- 6. Importul unui fișier CSV în pandas -----
print("\n*** 6. IMPORTUL FIȘIERELOR CSV ÎN PANDAS ***\n")

# Am încărcat deja df_vanzari și df_produse mai sus
# Încărcăm acum și celelalte fișiere

# Încărcăm date despre filiale
df_filiale = pd.read_csv("filiale.csv")

# Încărcăm date despre clienți
df_clienti = pd.read_csv("clienti.csv")

# Afișăm informații despre toate DataFrame-urile
print("Informații despre DataFrame-ul de vânzări:")
print(f"- Dimensiune: {df_vanzari.shape}")
print(f"- Coloane: {', '.join(df_vanzari.columns)}")
print(f"- Număr de înregistrări: {len(df_vanzari)}")

print("\nInformații despre DataFrame-ul de produse:")
print(f"- Dimensiune: {df_produse.shape}")
print(f"- Coloane: {', '.join(df_produse.columns)}")
print(f"- Număr de înregistrări: {len(df_produse)}")

print("\nInformații despre DataFrame-ul de filiale:")
print(f"- Dimensiune: {df_filiale.shape}")
print(f"- Coloane: {', '.join(df_filiale.columns)}")
print(f"- Număr de înregistrări: {len(df_filiale)}")

print("\nInformații despre DataFrame-ul de clienți:")
print(f"- Dimensiune: {df_clienti.shape}")
print(f"- Coloane: {', '.join(df_clienti.columns)}")
print(f"- Număr de înregistrări: {len(df_clienti)}")

print("\nPrimele 5 rânduri din DataFrame-ul de vânzări:")
print(df_vanzari.head())

# ----- 7. Accesarea datelor cu loc și iloc -----
print("\n*** 7. ACCESAREA DATELOR CU LOC ȘI ILOC ***\n")

# Accesăm primele 3 rânduri cu iloc
print("Primele 3 rânduri folosind iloc:")
print(df_vanzari.iloc[0:3])

# Accesăm anumite coloane cu iloc
print(
    "\nColoanele 'produs_nume', 'cantitate' și 'profit' pentru primele 3 rânduri folosind iloc:"
)
print(df_vanzari.iloc[0:3, [5, 9, 13]])

# Accesăm date folosind etichete cu loc
print("\nDate pentru categoria 'Electronice' folosind loc:")
print(
    df_vanzari.loc[
        df_vanzari["categorie"] == "Electronice", ["data", "produs_nume", "pret_total"]
    ].head()
)

# Accesăm date pentru anumite condiții cu loc
print("\nVânzările cu profit peste 2000 lei folosind loc:")
print(
    df_vanzari.loc[
        df_vanzari["profit"] > 2000, ["data", "produs_nume", "profit"]
    ].head()
)

# Accesare complexă: vânzări de produse electronice în luna mai cu discount
print("\nVânzări de produse electronice din luna mai cu discount:")
conditie = (
    (df_vanzari["categorie"] == "Electronice")
    & (df_vanzari["luna"] == "Mai")
    & (df_vanzari["discount"] > 0)
)
print(df_vanzari.loc[conditie, ["data", "produs_nume", "pret_total", "discount"]])

# ----- 8. Modificarea datelor în pandas -----
print("\n*** 8. MODIFICAREA DATELOR ÎN PANDAS ***\n")

# Facem o copie a DataFrame-ului pentru a nu modifica originalul
df_modificat = df_vanzari.copy()

# Adăugăm o coloană nouă pentru TVA (19% din prețul total)
df_modificat["tva"] = df_modificat["pret_total"] * 0.19
print("Adăugarea coloanei TVA:")
print(df_modificat[["produs_nume", "pret_total", "tva"]].head())

# Modificăm valorile existente - creștem prețul unitar cu 5%
df_modificat["pret_unitar_nou"] = df_modificat["pret_unitar"] * 1.05
print("\nCreșterea prețului unitar cu 5%:")
print(df_modificat[["produs_nume", "pret_unitar", "pret_unitar_nou"]].head())

# Recalculăm prețul total și profitul cu noile prețuri
df_modificat["pret_total_nou"] = (
    df_modificat["pret_unitar_nou"] * df_modificat["cantitate"]
)
df_modificat["profit_nou"] = df_modificat["pret_total_nou"] - df_modificat["cost_total"]
print("\nRecalcularea prețului total și a profitului:")
print(
    df_modificat[
        ["produs_nume", "pret_total", "pret_total_nou", "profit", "profit_nou"]
    ].head()
)


# Adăugăm o clasificare a valorii vânzării
def clasifica_valoare(pret):
    if pret < 1000:
        return "Mică"
    elif pret < 5000:
        return "Medie"
    else:
        return "Mare"


df_modificat["categorie_valoare"] = df_modificat["pret_total"].apply(clasifica_valoare)
print("\nAdăugarea clasificării valorii vânzării:")
print(df_modificat[["produs_nume", "pret_total", "categorie_valoare"]].head(10))

# ----- 9. Utilizarea funcțiilor de grup -----
print("\n*** 9. UTILIZAREA FUNCȚIILOR DE GRUP ***\n")

# Grupăm vânzările după categorie și calculăm suma vânzărilor
vanzari_per_categorie = (
    df_vanzari.groupby("categorie")["pret_total"].sum().reset_index()
)
print("Vânzări totale pe categorii:")
print(vanzari_per_categorie)

# Grupăm după produs și calculăm numărul de vânzări, valoarea medie și totală
analiza_per_produs = df_vanzari.groupby("produs_nume").agg(
    {"id": "count", "pret_total": ["mean", "sum"], "profit": ["mean", "sum"]}
)
analiza_per_produs.columns = [
    "numar_vanzari",
    "pret_mediu",
    "vanzari_totale",
    "profit_mediu",
    "profit_total",
]
print("\nAnaliză detaliată pe produse:")
print(analiza_per_produs)

# Grupăm după lună și an pentru a vedea evoluția vânzărilor
evolutie_lunara = df_vanzari.groupby(["an", "luna"])["pret_total"].sum().reset_index()
print("\nEvoluția vânzărilor lunare:")
print(evolutie_lunara)

# Grupăm după metodă de plată și calculăm statistici
analiza_plati = (
    df_vanzari.groupby("metoda_plata")
    .agg({"id": "count", "pret_total": "sum", "discount": "mean"})
    .reset_index()
)
analiza_plati.columns = [
    "metoda_plata",
    "numar_tranzactii",
    "valoare_totala",
    "discount_mediu",
]
print("\nAnaliză pe metode de plată:")
print(analiza_plati)

# Grupare complexă: analiză vânzări pe categorii, produse și luni
analiza_complexa = (
    df_vanzari.groupby(["categorie", "produs_nume", "luna"])
    .agg({"pret_total": "sum", "cantitate": "sum", "id": "count"})
    .reset_index()
    .rename(columns={"id": "numar_tranzactii"})
)
print("\nAnaliză complexă pe categorii, produse și luni (primele 10 rânduri):")
print(analiza_complexa.head(10))

# ----- 10. Tratarea valorilor lipsă -----
print("\n*** 10. TRATAREA VALORILOR LIPSĂ ***\n")

# Verificăm valorile lipsă în fiecare DataFrame
print("Numărul de valori lipsă în fiecare coloană din DataFrame-ul de vânzări:")
print(df_vanzari.isnull().sum())

# Verificăm înregistrările cu client_id lipsă
print("\nÎnregistrări cu client_id lipsă:")
print(
    df_vanzari[df_vanzari["client_id"].isnull()][
        ["id", "data", "produs_nume", "pret_total"]
    ]
)

# Facem o copie pentru a demonstra tratarea valorilor lipsă
df_fara_valori_lipsa = df_vanzari.copy()

# Metodă 1: Înlocuirea valorilor lipsă din client_id cu o valoare implicită (0)
df_fara_valori_lipsa["client_id_metoda1"] = df_fara_valori_lipsa["client_id"].fillna(0)

# Metodă 2: Înlocuirea valorilor lipsă din client_id cu media valorilor existente
client_id_mediu = int(df_fara_valori_lipsa["client_id"].mean())
df_fara_valori_lipsa["client_id_metoda2"] = df_fara_valori_lipsa["client_id"].fillna(
    client_id_mediu
)

print("\nÎnlocuirea valorilor lipsă:")
print(
    df_fara_valori_lipsa[df_fara_valori_lipsa["client_id"].isnull()][
        ["id", "client_id", "client_id_metoda1", "client_id_metoda2"]
    ]
)

# Metodă 3: Eliminarea rândurilor cu valori lipsă
df_fara_randuri_lipsa = df_vanzari.dropna(subset=["client_id"])
print(
    f"\nDimensiunea DataFrame-ului înainte de eliminarea rândurilor: {df_vanzari.shape}"
)
print(
    f"Dimensiunea DataFrame-ului după eliminarea rândurilor cu client_id lipsă: {df_fara_randuri_lipsa.shape}"
)

# Metodă 4: Imputarea valorilor lipsă folosind o valoare calculată (ID-ul filialei * 1000)
df_fara_valori_lipsa["client_id_metoda4"] = df_fara_valori_lipsa.apply(
    lambda row: (
        row["filiala_id"] * 1000 if pd.isnull(row["client_id"]) else row["client_id"]
    ),
    axis=1,
)
print("\nImputarea valorilor lipsă folosind o valoare calculată:")
print(
    df_fara_valori_lipsa[df_fara_valori_lipsa["client_id"].isnull()][
        ["id", "filiala_id", "client_id", "client_id_metoda4"]
    ]
)

# ----- 11. Ștergerea de coloane și înregistrări -----
print("\n*** 11. ȘTERGEREA DE COLOANE ȘI ÎNREGISTRĂRI ***\n")

# Ștergem coloanele care nu sunt necesare pentru analiză
df_curat = df_vanzari.copy()
coloane_de_sters = ["id", "filiala_id", "cost_total"]
df_curat = df_curat.drop(columns=coloane_de_sters)
print("DataFrame după ștergerea coloanelor nenecesare:")
print(f"Coloane înainte: {list(df_vanzari.columns)}")
print(f"Coloane după: {list(df_curat.columns)}")

# Ștergem înregistrările cu discount peste 10%
df_fara_discount_mare = df_curat[df_curat["discount"] <= 10]
print(f"\nNumăr de înregistrări înainte de filtrare: {df_curat.shape[0]}")
print(
    f"Număr de înregistrări după eliminarea celor cu discount > 10%: {df_fara_discount_mare.shape[0]}"
)

# Ștergem înregistrările pentru un anumit produs
df_fara_casti = df_curat[df_curat["produs_nume"] != "Căști wireless"]
print(
    f"\nNumăr de înregistrări după eliminarea produsului 'Căști wireless': {df_fara_casti.shape[0]}"
)

# Ștergerea selectivă: eliminăm vânzările cu valoare mică din luna ianuarie
conditie = ~((df_curat["luna"] == "Ianuarie") & (df_curat["pret_total"] < 1000))
df_filtrat_complex = df_curat[conditie]
print(
    f"\nNumăr de înregistrări după eliminarea vânzărilor mici din ianuarie: {df_filtrat_complex.shape[0]}"
)

# ----- 12. Prelucrări statistice, gruparea și agregarea datelor în pandas -----
print("\n*** 12. PRELUCRĂRI STATISTICE, GRUPAREA ȘI AGREGAREA DATELOR ***\n")

# Calculăm statistici descriptive pentru vânzări per categorie
statistici_categorii = df_vanzari.groupby("categorie").agg(
    {
        "pret_total": ["count", "min", "max", "mean", "sum", "std"],
        "profit": ["min", "max", "mean", "sum", "std"],
        "discount": ["mean", "max"],
    }
)

print("Statistici avansate pe categorii:")
print(statistici_categorii)

# Calculăm ponderea fiecărei categorii în vânzări
total_vanzari = df_vanzari["pret_total"].sum()
pondere_categorii = (
    df_vanzari.groupby("categorie")["pret_total"].sum() / total_vanzari * 100
)
pondere_categorii = pondere_categorii.reset_index()
pondere_categorii.columns = ["categorie", "pondere_procent"]

print("\nPonderea categoriilor în totalul vânzărilor:")
print(pondere_categorii)

# Analiza statistică a discounturilor
df_cu_discount = df_vanzari[df_vanzari["discount"] > 0]
statistici_discount = df_cu_discount.groupby("categorie")["discount"].agg(
    ["count", "mean", "min", "max"]
)
statistici_discount = statistici_discount.reset_index()
statistici_discount.columns = [
    "categorie",
    "numar_vanzari_cu_discount",
    "discount_mediu",
    "discount_minim",
    "discount_maxim",
]

print("\nStatistici privind discounturile pe categorii:")
print(statistici_discount)

# Calculăm corelația între variabile
corr = df_vanzari[
    ["cantitate", "pret_unitar", "pret_total", "profit", "discount"]
].corr()
print("\nMatricea de corelație:")
print(corr)

# ----- 13. Prelucrarea seturilor de date cu merge / join -----
print("\n*** 13. PRELUCRAREA SETURILOR DE DATE CU MERGE / JOIN ***\n")

# Combinăm DataFrame-urile pentru a obține informații complete despre vânzări și filiale
df_vanzari_filiale = pd.merge(
    df_vanzari, df_filiale, left_on="filiala_id", right_on="id", how="left"
)
df_vanzari_filiale = df_vanzari_filiale.rename(
    columns={"id_x": "id_vanzare", "id_y": "id_filiala"}
)
print("DataFrame combinat vânzări-filiale (primele 5 rânduri):")
print(
    df_vanzari_filiale[
        ["id_vanzare", "data", "produs_nume", "nume", "oras", "pret_total"]
    ].head()
)

# Combinăm vânzările cu informațiile despre clienți
df_vanzari_clienti = pd.merge(
    df_vanzari, df_clienti, left_on="client_id", right_on="id", how="left"
)
df_vanzari_clienti = df_vanzari_clienti.rename(
    columns={"id_x": "id_vanzare", "id_y": "id_client"}
)
print("\nDataFrame combinat vânzări-clienți (primele 5 rânduri):")
print(
    df_vanzari_clienti[
        ["id_vanzare", "data", "produs_nume", "gen", "varsta", "client_fidel"]
    ].head()
)

# Combinăm toate trei DataFrame-urile pentru o analiză completă
df_complet = pd.merge(
    df_vanzari_filiale, df_clienti, left_on="client_id", right_on="id", how="left"
)
df_complet = df_complet.rename(columns={"id": "id_client"})
print("\nDataFrame combinat complet (primele 5 rânduri):")
coloane_afisare = [
    "id_vanzare",
    "data",
    "produs_nume",
    "nume",
    "oras_x",
    "gen",
    "varsta",
    "client_fidel",
    "pret_total",
]
print(df_complet[coloane_afisare].head())

# Analiză avansată folosind DataFrame-ul combinat
# Vânzări per oraș și categorie de produse
vanzari_oras_categorie = (
    df_complet.groupby(["oras_x", "categorie"])["pret_total"].sum().reset_index()
)
vanzari_oras_categorie = vanzari_oras_categorie.rename(columns={"oras_x": "oras"})
print("\nVânzări pe orașe și categorii de produse:")
print(vanzari_oras_categorie)

# Analiza comportamentului clienților fideli vs. non-fideli
comportament_clienti = df_complet.groupby("client_fidel").agg(
    {"id_vanzare": "count", "pret_total": ["mean", "sum"], "discount": "mean"}
)
comportament_clienti.columns = [
    "numar_tranzactii",
    "valoare_medie",
    "valoare_totala",
    "discount_mediu",
]
print("\nComportamentul clienților fideli vs. non-fideli:")
print(comportament_clienti)

# ----- 14. Reprezentare grafică a datelor cu pachetul matplotlib -----
print("\n*** 14. REPREZENTARE GRAFICĂ A DATELOR CU MATPLOTLIB ***\n")

# Setăm stilul graficelor
plt.style.use("ggplot")

# Grafic 1: Vânzări pe categorii
vanzari_categorii = df_vanzari.groupby("categorie")["pret_total"].sum()
plt.figure(figsize=(10, 6))
vanzari_categorii.plot(kind="bar", color="skyblue")
plt.title("Vânzări totale pe categorii de produse")
plt.xlabel("Categorie")
plt.ylabel("Vânzări totale (lei)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("vanzari_categorii.png")
print("Grafic salvat: vanzari_categorii.png")

# Grafic 2: Evoluția vânzărilor lunare
vanzari_lunare = df_vanzari.groupby(["luna", "an"])["pret_total"].sum().reset_index()
# Ordonăm lunile cronologic
ordine_luni = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai"]
vanzari_lunare["luna"] = pd.Categorical(
    vanzari_lunare["luna"], categories=ordine_luni, ordered=True
)
vanzari_lunare = vanzari_lunare.sort_values("luna")

plt.figure(figsize=(12, 6))
plt.plot(
    range(len(vanzari_lunare)),
    vanzari_lunare["pret_total"],
    marker="o",
    linestyle="-",
    color="green",
)
plt.title("Evoluția vânzărilor lunare")
plt.xlabel("Luna")
plt.ylabel("Vânzări (lei)")
plt.xticks(
    range(len(vanzari_lunare)),
    [f"{row['luna']} {row['an']}" for _, row in vanzari_lunare.iterrows()],
    rotation=45,
)
plt.grid(True)
plt.tight_layout()
plt.savefig("evolutie_vanzari.png")
print("Grafic salvat: evolutie_vanzari.png")

# Grafic 3: Top 5 produse după profit
top_produse = (
    df_vanzari.groupby("produs_nume")["profit"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
plt.figure(figsize=(10, 6))
top_produse.plot(kind="barh", color="coral")
plt.title("Top 5 produse după profit total")
plt.xlabel("Profit total (lei)")
plt.ylabel("Produs")
plt.tight_layout()
plt.savefig("top_produse_profit.png")
print("Grafic salvat: top_produse_profit.png")

# Grafic 4: Distribuția metodelor de plată
metode_plata_counts = df_vanzari["metoda_plata"].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(
    metode_plata_counts,
    labels=metode_plata_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    shadow=True,
    colors=["#ff9999", "#66b3ff", "#99ff99"],
)
plt.axis("equal")
plt.title("Distribuția metodelor de plată")
plt.tight_layout()
plt.savefig("distributie_metode_plata.png")
print("Grafic salvat: distributie_metode_plata.png")

# Grafic 5: Comparație între vânzări și profit pentru fiecare categorie
vanzari_profit_categorie = (
    df_vanzari.groupby("categorie")
    .agg({"pret_total": "sum", "profit": "sum"})
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(vanzari_profit_categorie))
width = 0.35

ax.bar(
    [i - width / 2 for i in x],
    vanzari_profit_categorie["pret_total"],
    width,
    label="Vânzări",
    color="blue",
)
ax.bar(
    [i + width / 2 for i in x],
    vanzari_profit_categorie["profit"],
    width,
    label="Profit",
    color="green",
)

ax.set_ylabel("Valoare (lei)")
ax.set_title("Comparație între vânzări și profit pe categorii")
ax.set_xticks(x)
ax.set_xticklabels(vanzari_profit_categorie["categorie"])
ax.legend()

plt.tight_layout()
plt.savefig("comparatie_vanzari_profit.png")
print("Grafic salvat: comparatie_vanzari_profit.png")

# ----- 15. Utilizarea pachetului scikit-learn (clusterizare, regresie logistică) -----
print("\n*** 15. UTILIZAREA PACHETULUI SCIKIT-LEARN ***\n")

# Pregătim datele pentru clusterizare
df_cluster = (
    df_vanzari.groupby("produs_nume")
    .agg({"pret_total": "sum", "profit": "sum", "cantitate": "sum"})
    .reset_index()
)

X = df_cluster[["pret_total", "profit"]].values

# Aplicăm algoritmul K-means cu 3 clustere
kmeans = KMeans(n_clusters=3, random_state=42)
df_cluster["cluster"] = kmeans.fit_predict(X)

print("Rezultatele clusterizării produselor:")
print(df_cluster[["produs_nume", "pret_total", "profit", "cluster"]])

# Vizualizăm clusterele
plt.figure(figsize=(10, 6))
colors = ["red", "green", "blue"]
for i in range(3):
    plt.scatter(
        df_cluster[df_cluster["cluster"] == i]["pret_total"],
        df_cluster[df_cluster["cluster"] == i]["profit"],
        s=100,
        c=colors[i],
        label=f"Cluster {i+1}",
    )

plt.scatter(
    kmeans.cluster_centers_[:, 0],
    kmeans.cluster_centers_[:, 1],
    s=300,
    c="yellow",
    marker="*",
    label="Centroide",
)
plt.title("Clusterizarea produselor după vânzări și profit")
plt.xlabel("Vânzări totale (lei)")
plt.ylabel("Profit total (lei)")
plt.legend()
plt.grid(True)
plt.savefig("clusterizare_produse.png")
print("Grafic salvat: clusterizare_produse.png")

# Regresie logistică pentru a prezice probabilitatea de discount
df_regresie = df_vanzari.copy()
df_regresie["are_discount"] = (df_regresie["discount"] > 0).astype(int)

# Asigurăm-ne că toate coloanele sunt numerice
df_regresie["pret_total"] = pd.to_numeric(df_regresie["pret_total"])
df_regresie["cantitate"] = pd.to_numeric(df_regresie["cantitate"])

# Codificăm variabilele categorice
df_regresie = pd.get_dummies(
    df_regresie, columns=["categorie", "metoda_plata"], drop_first=True
)

# Selectăm variabilele independente
X_cols = [
    "pret_total",
    "cantitate",
    "categorie_Electronice",
    "categorie_Electrocasnice",
    "metoda_plata_Numerar",
    "metoda_plata_Transfer bancar",
]
X = df_regresie[X_cols]
y = df_regresie["are_discount"]

# Antrenăm modelul de regresie logistică
model = LogisticRegression(random_state=42)
model.fit(X, y)

# Afișăm coeficienții modelului
coeficienti = pd.DataFrame({"Variabilă": X.columns, "Coeficient": model.coef_[0]})
print("\nCoeficienții modelului de regresie logistică pentru predicția discountului:")
print(coeficienti)

# Calculăm acuratețea modelului
y_pred = model.predict(X)
acuratete = (y == y_pred).mean()
print(f"\nAcuratețea modelului de regresie logistică: {acuratete:.4f}")

# Interpretarea modelului: calcularea probabilității de discount pentru diferite scenarii
print("\nProbabilități de discount pentru diferite scenarii:")
# Scenariu 1: Vânzare electrocasnice, valoare mică, numerar
scenariu1 = pd.DataFrame([[1000, 1, 0, 1, 1, 0]], columns=X_cols)
prob1 = model.predict_proba(scenariu1)[0, 1]
print(f"Scenariu 1 (Electrocasnice, 1000 lei, numerar): {prob1:.2f}")

# Scenariu 2: Vânzare electronice, valoare mare, card
scenariu2 = pd.DataFrame([[5000, 2, 1, 0, 0, 0]], columns=X_cols)
prob2 = model.predict_proba(scenariu2)[0, 1]
print(f"Scenariu 2 (Electronice, 5000 lei, card): {prob2:.2f}")

# Scenariu 3: Vânzare accesorii, valoare mică, transfer bancar
scenariu3 = pd.DataFrame([[500, 1, 0, 0, 0, 1]], columns=X_cols)
prob3 = model.predict_proba(scenariu3)[0, 1]
print(f"Scenariu 3 (Accesorii, 500 lei, transfer bancar): {prob3:.2f}")

# ----- 16. Utilizarea pachetului statsmodels (regresie multiplă) -----
print("\n*** 16. UTILIZAREA PACHETULUI STATSMODELS ***\n")

# Pregătim datele pentru regresie multiplă
df_regresie_multipla = df_vanzari.copy()

# Asigurăm-ne că avem doar tipuri de date numerice pentru regresie
df_regresie_multipla["cantitate"] = pd.to_numeric(df_regresie_multipla["cantitate"])
df_regresie_multipla["discount"] = pd.to_numeric(df_regresie_multipla["discount"])
df_regresie_multipla["profit"] = pd.to_numeric(df_regresie_multipla["profit"])

# Codificăm variabilele categorice
df_regresie_multipla = pd.get_dummies(
    df_regresie_multipla, columns=["categorie", "metoda_plata"], drop_first=True
)

# Selectăm variabilele independente (predictori) și dependente (target)
X = df_regresie_multipla[
    [
        "cantitate",
        "discount",
        "categorie_Electronice",
        "categorie_Electrocasnice",
        "metoda_plata_Numerar",
        "metoda_plata_Transfer bancar",
    ]
]

# Verificăm dacă toate coloanele din X sunt numerice
print("Tipurile de date în X:")
print(X.dtypes)

# Convertim explicit toate coloanele la float64
X = X.astype(float)

# Adăugăm constanta (interceptul)
X = sm.add_constant(X)

# Asigurăm-ne că y este de tip numeric
y = pd.to_numeric(df_regresie_multipla["profit"])

# Antrenăm modelul de regresie multiplă
try:
    model = sm.OLS(y, X).fit()

    # Afișăm sumarul modelului
    print("Sumarul modelului de regresie multiplă pentru predicția profitului:")
    print(model.summary())

    # Facem predicții cu modelul
    df_regresie_multipla["profit_prezis"] = model.predict(X)

    # Vizualizăm relația între profitul real și cel prezis
    plt.figure(figsize=(10, 6))
    plt.scatter(
        df_regresie_multipla["profit"], df_regresie_multipla["profit_prezis"], alpha=0.5
    )
    plt.plot([y.min(), y.max()], [y.min(), y.max()], "k--", lw=2)
    plt.xlabel("Profit real (lei)")
    plt.ylabel("Profit prezis (lei)")
    plt.title("Relația între profitul real și cel prezis de model")
    plt.grid(True)
    plt.savefig("regresie_profit.png")
    print("Grafic salvat: regresie_profit.png")

    # Analiza importanței variabilelor
    coeficienti_regresie = pd.DataFrame(
        {
            "Variabilă": X.columns,
            "Coeficient": model.params,
            "P-value": model.pvalues,
            "Semnificativ": model.pvalues < 0.05,
        }
    )
    print("\nImportanța variabilelor în modelul de regresie multiplă:")
    print(coeficienti_regresie)

    # Utilizarea modelului pentru predicții în scenarii noi
    print("\nPredicția profitului pentru scenarii noi:")

    # Scenariu 1: Vânzare 2 laptopuri electronice cu discount 5%, plată cu card
    scenariu1 = np.array([1, 2, 5, 1, 0, 0, 0]).reshape(1, -1)
    profit_prezis1 = model.predict(scenariu1)[0]
    print(
        f"Scenariu 1 (2 produse electronice, discount 5%, card): {profit_prezis1:.2f} lei"
    )

    # Scenariu 2: Vânzare 3 frigidere electrocasnice fără discount, plată cu numerar
    scenariu2 = np.array([1, 3, 0, 0, 1, 1, 0]).reshape(1, -1)
    profit_prezis2 = model.predict(scenariu2)[0]
    print(
        f"Scenariu 2 (3 produse electrocasnice, fără discount, numerar): {profit_prezis2:.2f} lei"
    )

    # Scenariu 3: Vânzare 1 produs accesoriu cu discount 10%, plată prin transfer bancar
    scenariu3 = np.array([1, 1, 10, 0, 0, 0, 1]).reshape(1, -1)
    profit_prezis3 = model.predict(scenariu3)[0]
    print(
        f"Scenariu 3 (1 produs accesoriu, discount 10%, transfer bancar): {profit_prezis3:.2f} lei"
    )

except Exception as e:
    print(f"Eroare la modelul de regresie: {str(e)}")
    print("Implementăm o abordare alternativă pentru regresie utilizând scikit-learn:")

    from sklearn.linear_model import LinearRegression

    # Folosim scikit-learn pentru regresie multiplă
    X_sklearn = df_regresie_multipla[
        [
            "cantitate",
            "discount",
            "categorie_Electronice",
            "categorie_Electrocasnice",
            "metoda_plata_Numerar",
            "metoda_plata_Transfer bancar",
        ]
    ]
    y_sklearn = df_regresie_multipla["profit"]

    # Antrenăm modelul
    lr_model = LinearRegression()
    lr_model.fit(X_sklearn, y_sklearn)

    # Afișăm coeficienții
    coeficienti = pd.DataFrame(
        {"Variabilă": X_sklearn.columns, "Coeficient": lr_model.coef_}
    )
    print("\nCoeficienții modelului de regresie liniară (scikit-learn):")
    print(coeficienti)
    print(f"Intercept: {lr_model.intercept_:.2f}")

    # Evaluăm performanța modelului
    y_pred = lr_model.predict(X_sklearn)
    r2 = lr_model.score(X_sklearn, y_sklearn)
    print(f"\nR² (coeficient de determinare): {r2:.4f}")

    # Facem predicții pentru scenarii
    print("\nPredicția profitului pentru scenarii noi:")

    # Scenariu 1: Vânzare 2 laptopuri electronice cu discount 5%, plată cu card
    scenariu1 = np.array([[2, 5, 1, 0, 0, 0]])
    profit_prezis1 = lr_model.predict(scenariu1)[0]
    print(
        f"Scenariu 1 (2 produse electronice, discount 5%, card): {profit_prezis1:.2f} lei"
    )

    # Scenariu 2: Vânzare 3 frigidere electrocasnice fără discount, plată cu numerar
    scenariu2 = np.array([[3, 0, 0, 1, 1, 0]])
    profit_prezis2 = lr_model.predict(scenariu2)[0]
    print(
        f"Scenariu 2 (3 produse electrocasnice, fără discount, numerar): {profit_prezis2:.2f} lei"
    )

    # Scenariu 3: Vânzare 1 produs accesoriu cu discount 10%, plată prin transfer bancar
    scenariu3 = np.array([[1, 10, 0, 0, 0, 1]])
    profit_prezis3 = lr_model.predict(scenariu3)[0]
    print(
        f"Scenariu 3 (1 produs accesoriu, discount 10%, transfer bancar): {profit_prezis3:.2f} lei"
    )

# ----- Sumar și recomandări finale -----
print("\n=== SUMAR ȘI RECOMANDĂRI FINALE ===\n")

# Top produse după profit
top_produse_profit = (
    df_vanzari.groupby("produs_nume")["profit"].sum().sort_values(ascending=False)
)
print("Top 3 produse după profit total:")
print(top_produse_profit.head(3))

# Top categorii după vânzări
top_categorii = (
    df_vanzari.groupby("categorie")["pret_total"].sum().sort_values(ascending=False)
)
print("\nCategoriile după vânzări totale:")
print(top_categorii)

# Calculăm marjele de profit medii pe categorii
marja_profit_categorii = df_vanzari.groupby("categorie").agg(
    {"pret_total": "sum", "cost_total": "sum"}
)
marja_profit_categorii["marja_profit_procent"] = (
    (marja_profit_categorii["pret_total"] - marja_profit_categorii["cost_total"])
    / marja_profit_categorii["pret_total"]
    * 100
).round(2)
print("\nMarje de profit medii pe categorii:")
print(marja_profit_categorii[["marja_profit_procent"]])

# Distribuția vânzărilor pe orașe (filiale)
vanzari_orase = (
    df_vanzari_filiale.groupby("oras")["pret_total"].sum().sort_values(ascending=False)
)
print("\nDistribuția vânzărilor pe orașe:")
print(vanzari_orase)

# Recomandări pe baza analizelor efectuate
print("\nRecomandări pentru extinderea afacerii:")
print("1. Focalizarea pe produsele din clusterul cu profitabilitate ridicată")
print(
    "2. Extinderea ofertei de produse electronice, care generează marje de profit bune"
)
print(
    "3. Optimizarea politicii de discount, concentrarea pe produsele care generează vânzări adiționale"
)
print("4. Extinderea în orașe cu performanță ridicată a filialelor existente")
print(
    "5. Investiția în marketing pentru produsele cu potențial de creștere identificate prin modelele predictive"
)
print(
    "6. Dezvoltarea programului de fidelizare a clienților, care aduce vânzări cu valoare mai mare"
)
print(
    "7. Optimizarea metodelor de plată și oferiea de facilități pentru metodele preferate de clienți"
)

print(
    "\nProiect realizat cu succes, toate cele 16 facilități Python au fost implementate!"
)
