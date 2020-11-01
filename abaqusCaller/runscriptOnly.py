import csv
import subprocess
# stdout = subprocess.PIPE, stderr = subprocess.PIPE
subprocess.run(
    ["abaqus", "cae", "noGUI=./abaqusScript/autoParametric2DnoGUI.py"], shell=True)
print("*********************")
with open('force_output.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        for col in row:
            print(float(col))
