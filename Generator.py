
import pulp as lp
import random
import pandas as pd
import numpy as np


filepath = "/content/Data assignment operating room 2 Large with keys.2.0.xlsx" #overal filepath neerzetten
excel_df1 = pd.read_excel(filepath, sheet_name = 0, header = None)
excel_df2 = pd.read_excel(filepath, sheet_name = 1)
excel_df3 = pd.read_excel(filepath, sheet_name = 2)
surgeries = excel_df2["Surgery"]


# Dictionary = operaties met kans en minuten
surgery_types = {
    0: {"kans": 0.214, "duur": (283.25, 140.52)}, #hart en vaat
    1: {"kans": 0.099, "duur": (228.18, 110.30)}, #heup en knie
    2: {"kans": 0.092, "duur": (116.90, 78.90)}, #Laparoscopische buikingrepen
    3: {"kans": 0.105, "duur": (218.01, 113.73)}, #overige buikchirurgie
    4: {"kans": 0.076, "duur": (194.88, 98.54)}, #KNO
    5: {"kans": 0.090, "duur": (166.51, 103.46)}, #keizersnee & spataderen
    6: {"kans": 0.324, "duur": (184.88, 100.25)}, #staar & meniscus
}

# Operaties en kansen opslaan
types = list(surgery_types.keys())
kansen = [surgery_types[t]["kans"] for t in types]

# elke operatie type en tijd geven
namen = []
duur_lijst = [] # Renamed to avoid conflict with the integer 'duur' variable inside the loop

for i in surgeries:
  operatie_type = random.choices(types, weights=kansen)[0]
  mean, stdev = surgery_types[operatie_type]["duur"]
  # current_duur = random.randint(min_tijd, max_tijd)
  current_duur = min(max(np.random.normal(),-2), 2)*stdev+mean
  while current_duur < 0:
    current_duur =min(max(np.random.normal(),-2), 2)*stdev+mean

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
