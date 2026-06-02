import pulp as lp
import random
import pandas as pd

filepath = "/Data assignment operating room 2 Large with keys.xlsx" #overal filepath neerzetten
excel_df1 = pd.read_excel(filepath, sheet_name = 0, header = None)
excel_df2 = pd.read_excel(filepath, sheet_name = 1)
excel_df3 = pd.read_excel(filepath, sheet_name = 2)
surgeries = excel_df2["Surgery"]


# Dictionary = operaties met kans en minuten
surgery_types = {
    0: {"kans": 0.214, "duur": (180, 240)}, #hart en vaat
    1: {"kans": 0.099, "duur": (60, 120)}, #heup en knie
    2: {"kans": 0.092, "duur": (45, 90)}, #Laparoscopische buikingrepen
    3: {"kans": 0.105, "duur": (60, 120)}, #overige buikchirurgie
    4: {"kans": 0.076, "duur": (30, 45)}, #KNO
    5: {"kans": 0.090, "duur": (30, 45)}, #keizersnee
    6: {"kans": 0.324, "duur": (15, 20)}, #staar
}

# Operaties en kansen opslaan
types = list(surgery_types.keys())
kansen = [surgery_types[t]["kans"] for t in types]

# elke operatie type en tijd geven
namen = []
duur_lijst = [] # Renamed to avoid conflict with the integer 'duur' variable inside the loop

for i in surgeries:
  operatie_type = random.choices(types, weights=kansen)[0]
  min_tijd, max_tijd = surgery_types[operatie_type]["duur"]
  current_duur = random.randint(min_tijd, max_tijd) # Store generated duration in a temporary variable

  namen.append(operatie_type)
  duur_lijst.append(current_duur) # Append the current_duur to the list

# Toevoegen
excel_df2["Duration"] = duur_lijst
excel_df2["Keys"] = namen

# nieuwe excel met operatie types en tijdsduur terug opslaan onder nieuwe naam
with pd.ExcelWriter("/excel_df2_updated.xlsx") as writer:
    excel_df1.to_excel(writer, sheet_name = "Sheet0", index=False, header = None)
    excel_df2.to_excel(writer, sheet_name = "Sheet1", index=False)
    excel_df3.to_excel(writer, sheet_name = "Sheet2", index=False)


print(excel_df2.head())