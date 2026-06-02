
import pulp as lp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# collect per-room overtime from the solution
# For the small, change s_large to s_small
def graph(x, durations, surgeries, dayno, roomno, capacity):
    surgery_load = np.array([
        [[lp.value(x[i][r][t]) * durations.iloc[i] for i in range(len(surgeries))]
        for t in range(dayno)]
        for r in range(roomno)
    ])

    fig, axes = plt.subplots(1, dayno, figsize=(5 * dayno, 6), sharey=True)
    if dayno == 1:
        axes = [axes]

    cmap = plt.get_cmap("tab20")
    surgery_colors = [cmap(i % 20) for i in range(len(surgeries))]

    for t, ax in enumerate(axes):
        for r in range(roomno):
            bottom = 0
            for i in range(len(surgeries)):
                height = surgery_load[r][t][i]
                if height > 0:
                    ax.bar(r, height, bottom=bottom, color=surgery_colors[i], edgecolor="white", linewidth=0.5)
                    ax.text(r, bottom + height / 2, f"S{i+1}", ha="center", va="center", fontsize=7, color="white")
                    bottom += height

        # draw capacity line
        ax.axhline(capacity, color="black", linestyle="--", linewidth=1, label="Capacity")
        ax.text(roomno - 0.5, capacity + 2, f"{capacity} min", color="red", fontsize=8, va="bottom", ha="left")
        ax.set_title(f"Day {t+1}")
        ax.set_xticks(range(roomno))
        ax.set_xticklabels([f"Room {r+1}" for r in range(roomno)])
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Minutes")
    fig.suptitle("Surgery schedule per room per day (ILP with keys)", y=0.95, fontsize=20)

    # legend
    handles = [plt.Rectangle((0,0),1,1, color=surgery_colors[i]) for i in range(len(surgeries))]
    labels = [f"S{i+1}: {surgeries.iloc[i]}" for i in range(len(surgeries))]
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(1.15, 0.5), fontsize=8, title="Surgery")

    plt.show()

def ILP(filepath):
  df1 = pd.read_excel(filepath, sheet_name = 0, header = None)
  df2 = pd.read_excel(filepath, sheet_name = 1)
  df3 = pd.read_excel(filepath, sheet_name = 2)

  df1.columns = ["label","value"]

  capacity = df1.loc[df1["label"] == "Capacity", "value"].values[0]
  roomno = df1.loc[df1["label"] == "Number operating rooms", "value"].values[0]
  dayno = df1.loc[df1["label"] == "Number days", "value"].values[0]

  surgeries = df2["Surgery"]
  durations = df2["Duration"]
  keys = df2["Keys"]

  allowed = df3.iloc[:, 2:].values

  # defining LP
  OR_relaxation = lp.LpProblem("OR_relaxation_small", sense = lp.LpMinimize)

  # defining decision variables
  x_vals = lp.LpVariable.dicts("x_vals", (range(len(surgeries)), range(roomno), range(dayno)), cat = "Binary")
  s_vals = lp.LpVariable.dicts("s_vals", (range(roomno), range(dayno)), lowBound = (-1) * capacity, upBound = capacity, cat = "Continuous")
  z_vals = lp.LpVariable.dicts("z_vals", range(dayno), lowBound = 0, upBound = capacity, cat = "Continuous")

  OR_relaxation += lp.lpSum([z_vals[t] for t in range(dayno)])

  # setting constraints room capacity
  for r in range(roomno):
      for t in range(dayno):
          OR_relaxation += lp.lpSum([durations.iloc[i] * x_vals[i][r][t] for i in range(len(durations))]) - s_vals[r][t] == capacity

  # setting surgery completion constraints
  for i in range(len(surgeries)):
      x = keys[i]
      OR_relaxation += lp.lpSum([x_vals[i][r][t]*allowed[x][r] for r in range(roomno) for t in range(dayno)]) == 1

  # setting constraints maximum overtime
  for r in range(roomno):
      for t in range(dayno):
          OR_relaxation += z_vals[t] - s_vals[r][t] >= 0

  # solve command and printed results for data set
  OR_relaxation.solve()
  print("Data set solution status: ", lp.LpStatus[OR_relaxation.status])
  print("Data set overtime sum: ", lp.value(OR_relaxation.objective))

  # prints decision variables that represent maximum overtime on a day in a list for each day
  overtime_list = [lp.value(z_vals[t]) for t in range(dayno)]
  print(overtime_list)

  # prints the x[i][r][t] values for the data set
  print("x[i][r][t] values for data set")
  for i in range(len(surgeries)):
      surgery_list = [[lp.value(x_vals[i][r][t]) for r in range(roomno)] for t in range(dayno)]
      print(surgery_list)
    
  graph(x_vals, durations, surgeries, dayno, roomno, capacity)


filepath = "/Users/daangeijsen/Programming/TW/TW-modeleren/Modeleren 2/Operation/Data assignment operating room 2 Small with keys.xlsx"
ILP(filepath)
