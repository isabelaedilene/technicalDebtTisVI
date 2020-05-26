from csv import writer

import pandas as pd

with open("../Sonar/analiseSonar.csv", "r", encoding="utf-8") as f:
    csv_string = f.read()

with open("sonar_analysis.csv", "w", encoding="utf-8") as f:
    csv = writer(f)
    for line in csv_string.splitlines():
        csv.writerow(line.strip('"').split(","))

satd = pd.read_csv("satd_files.csv")
sonar = pd.read_csv("sonar_analysis.csv")

satd_files = satd["file_path"].to_list()

sonar_satd = sonar[sonar.file_path.isin(satd_files) & sonar.code_smells > 0]
sonar_satd_not = sonar[~sonar.file_path.isin(satd_files) & sonar.code_smells > 0]

sonar_satd.to_csv("results_satd.csv")
sonar_satd_not.to_csv("results_not_satd.csv")

print(f"Sonar SATDs                 = {len(sonar_satd)}")
print(f"Sonar Total                 = {len(sonar)}")
print(f"SATDs/Total                 = {len(sonar_satd)/len(sonar)*1e2 :.3}%")
print(f"SATD Mean NcLoc             = {sonar_satd.ncloc.mean()}")
print(f"SATD Mean Ciclomatic        = {sonar_satd.ciclomatic.mean()}")
print(f"SATD Mean Cognitive         = {sonar_satd.cognitive.mean()}")
print(f"SATD Mean Code Smells       = {sonar_satd.code_smells.mean()}")
print(f"SATD Median NcLoc           = {sonar_satd.ncloc.median()}")
print(f"SATD Median Ciclomatic      = {sonar_satd.ciclomatic.median()}")
print(f"SATD Median Cognitive       = {sonar_satd.cognitive.median()}")
print(f"SATD Median Code Smells     = {sonar_satd.code_smells.median()}")
print(f"Not SATD Mean NcLoc         = {sonar_satd_not.ncloc.mean()}")
print(f"Not SATD Mean Ciclomatic    = {sonar_satd_not.ciclomatic.mean()}")
print(f"Not SATD Mean Cognitive     = {sonar_satd_not.cognitive.mean()}")
print(f"Not SATD Mean Code Smells   = {sonar_satd_not.code_smells.mean()}")
print(f"Not SATD Median NcLoc       = {sonar_satd_not.ncloc.median()}")
print(f"Not SATD Median Ciclomatic  = {sonar_satd_not.ciclomatic.median()}")
print(f"Not SATD Median Cognitive   = {sonar_satd_not.cognitive.median()}")
print(f"Not SATD Median Code Smells = {sonar_satd_not.code_smells.median()}")
