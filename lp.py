import pulp as lp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PATH_SMALL = "/Users/daangeijsen/Programming/TW/TW-modeleren/Modeleren 2/Operation/Data assignment operating room 2 Small.xlsx"
PATH_LARGE = "/Users/daangeijsen/Programming/TW/TW-modeleren/Modeleren 2/Operation/Data assignment operating room 2 Large.xlsx"

# -- ADJUST FILE PATH TO OWN -- importing sheet 1 and 2 of the small excel sheet
sdf1 = pd.read_excel(PATH_SMALL, sheet_name = 0, header = None)
sdf2 = pd.read_excel(PATH_SMALL, sheet_name = 1)

# -- ADJUST FILE PATH TO OWN -- importing sheet 1 and 2 of the large excel sheet
ldf1 = pd.read_excel(PATH_LARGE, sheet_name = 0, header = None)
ldf2 = pd.read_excel(PATH_LARGE, sheet_name = 1)

# labelling columns on the 1st sheets separately because they are a bit unpleasantly formatted
sdf1.columns = ["label","value"]
ldf1.columns = ["label","value"]

# setting relevant numerical values for respective data sets, returns integers
scapacity = sdf1.loc[sdf1["label"] == "Capacity", "value"].values[0]
lcapacity = ldf1.loc[ldf1["label"] == "Capacity", "value"].values[0]

sroomno = sdf1.loc[sdf1["label"] == "Number operating rooms", "value"].values[0]
lroomno = ldf1.loc[ldf1["label"] == "Number operating rooms", "value"].values[0]

sdayno = sdf1.loc[sdf1["label"] == "Number days", "value"].values[0]
ldayno = ldf1.loc[ldf1["label"] == "Number days", "value"].values[0]

# setting variables that take columns, returns pandas series
ssurgeries = sdf2["Surgery"]
sdurations = sdf2["Duration"]

lsurgeries = ldf2["Surgery"]
ldurations = ldf2["Duration"]

# { -------------------------------------------- } Small data set LP relaxation

# defining LP for small data set
OR_relaxation_small = lp.LpProblem("OR_relaxation_small", sense = lp.LpMinimize)

# defining decision variables for small data set
x_small = lp.LpVariable.dicts("x_small", (range(len(ssurgeries)), range(sroomno), range(sdayno)), lowBound = 0, upBound = 1, cat = "Continuous")
s_small = lp.LpVariable.dicts("s_small", (range(sroomno), range(sdayno)), lowBound = (-1) * scapacity, upBound = scapacity, cat = "Continuous")
z_small = lp.LpVariable.dicts("z_small", range(sdayno), lowBound = 0, upBound = scapacity, cat = "Continuous")

# setting objective function for small dataset
OR_relaxation_small += lp.lpSum([z_small[i] for i in range(sdayno)]), "Overtime small data set"

# setting constraints room capacity for small data set
for r in range(sroomno):
    for t in range(sdayno):
        OR_relaxation_small += lp.lpSum([sdurations.iloc[i] * x_small[i][r][t] for i in range(len(sdurations))]) - s_small[r][t] == scapacity

# setting surgery completion constraints for small data set
for i in range(len(ssurgeries)):
    OR_relaxation_small += lp.lpSum([x_small[i][r][t] for r in range(sroomno) for t in range(sdayno)]) == 1

# setting constraints maximum overtime for small data set
for r in range(sroomno):
    for t in range(sdayno):
        OR_relaxation_small += z_small[t] - s_small[r][t] >= 0

# solve command and printed results for small data set
OR_relaxation_small.solve()
print("Small data set solution status: ", lp.LpStatus[OR_relaxation_small.status])
print("Small data set overtime sum: ", lp.value(OR_relaxation_small.objective))

# prints decision variables that represent maximum overtime on a day in a list for each day
sovertime_list = [lp.value(z_small[t]) for t in range(sdayno)]
print(sovertime_list)

# prints the x[i][r][t] values for the small data set, commented out because of clutter, if you're using VSCode just select the 3 lines below and use Ctrl + / if you want to run them
# for i in range(len(ssurgeries)):
#     ssurgery_list = [[lp.value(x_small[i][r][t]) for r in range(sroomno)] for t in range(sdayno)]
#     print(ssurgery_list)

# { -------------------------------------------- } Large data set LP relaxation

# defining LP for large data set
OR_relaxation_large = lp.LpProblem("OR_relaxation_large", sense = lp.LpMinimize)

# defining decision variables for large data set
x_large = lp.LpVariable.dicts("x_large", (range(len(lsurgeries)), range(lroomno), range(ldayno)), lowBound = 0, upBound = 1, cat = "Continuous")
s_large = lp.LpVariable.dicts("s_large", (range(lroomno), range(ldayno)), lowBound = (-1) * lcapacity, upBound = lcapacity, cat = "Continuous")
z_large = lp.LpVariable.dicts("z_large", range(ldayno), lowBound = 0, upBound = lcapacity, cat = "Continuous")

# setting objective function for large dataset
OR_relaxation_large += lp.lpSum([z_large[i] for i in range(ldayno)]), "Overtime large data set"

# setting constraints room capacity for large data set
for r in range(lroomno):
    for t in range(ldayno):
        OR_relaxation_large += lp.lpSum([ldurations.iloc[i] * x_large[i][r][t] for i in range(len(ldurations))]) - s_large[r][t] == lcapacity

# setting surgery completion constraints for large data set
for i in range(len(lsurgeries)):
    OR_relaxation_large += lp.lpSum([x_large[i][r][t] for r in range(lroomno) for t in range(ldayno)]) == 1

# setting constraints maximum overtime for large data set
for r in range(lroomno):
    for t in range(ldayno):
        OR_relaxation_large += z_large[t] - s_large[r][t] >= 0

# solve command and printed results for large data set
OR_relaxation_large.solve()
print("Large data set solution status: ", lp.LpStatus[OR_relaxation_large.status])
print("Large data set overtime sum: ", lp.value(OR_relaxation_large.objective))

# prints decision variables that represent maximum overtime on a day in a list for each day
lovertime_list = [lp.value(z_large[t]) for t in range(ldayno)]
print(lovertime_list)

# prints the x[i][r][t] values for the large data set
print("x[i][r][t] values for large data set")
for i in range(len(lsurgeries)):
    lsurgery_list = [[lp.value(x_large[i][r][t]) for r in range(lroomno)] for t in range(ldayno)]
    print(lsurgery_list)

# Notice in the large data set that in a solution where we spread each surgery evenly across every room, we get a maximum overtime of 14.5 on day 1 and day 2 resp., summing to 29.
# From this, we can see that z_large[day 1] = 0, z_large[day 2] = 29 is a solution that is equivalent (overtime sum of 0 + 29 = 29) to the one we can intuitively reason is optimal.
# Because there are then at least 2 optimal solutions, the suspicion that in this LP relaxation there are infinitely many optimal solutions is confirmed.

# From the x[i][r][t] values notice that indeed not all of them satisfy the integrality constraints we otherwise impose.
