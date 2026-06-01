
import pulp as lp
import pandas as pd

def ILP(filepath):
  df1 = pd.read_excel(filepath, sheet_name = 0, header = None)
  df2 = pd.read_excel(filepath, sheet_name = 1)

  df1.columns = ["label","value"]

  capacity = df1.loc[df1["label"] == "Capacity", "value"].values[0]
  roomno = df1.loc[df1["label"] == "Number operating rooms", "value"].values[0]
  dayno = df1.loc[df1["label"] == "Number days", "value"].values[0]

  surgeries = df2["Surgery"]
  durations = df2["Duration"]

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
      OR_relaxation += lp.lpSum([x_vals[i][r][t] for r in range(roomno) for t in range(dayno)]) == 1

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


