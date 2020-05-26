from csv import writer

import pandas as pd

with open("../Sonar/analiseSonar.csv", "r", encoding="utf-8") as f:
    csv_string = f.read()

with open("sonar_analysis.csv", "w", encoding="utf-8") as f:
    csv = writer(f)
    for line in csv_string.splitlines():
        csv.writerow(line.strip('"').split(","))

satd_dirty = pd.read_csv("satd_files_full.csv")
sonar = pd.read_csv("sonar_analysis.csv")
sonar_projects = sonar.project.drop_duplicates().to_list()
satd = satd_dirty[satd_dirty.name.isin(sonar_projects)]
satd.to_csv("satd_files.csv")
# print(len(satd)/len(satd_dirty))
# print(len(satd_dirty) - len(satd))

satd_files = satd["file_path"].to_list()

sonar_satd = sonar[sonar.file_path.isin(satd_files)]
sonar_codesmells = sonar[sonar.code_smells > 0]
sonar_not_satd = sonar[~sonar.file_path.isin(satd_files) & sonar.code_smells > 0]
sonar_codesmells_satd = sonar[sonar.file_path.isin(satd_files) & sonar.code_smells > 0]
sonar_not_codesmells_satd = sonar[sonar.file_path.isin(satd_files) & sonar.code_smells == 0]

sonar_satd.to_csv("results_sonar_satd.csv")
sonar_not_satd.to_csv("results_sonar_not_satd.csv")
sonar_codesmells.to_csv("results_sonar_codesmells.csv")
sonar_codesmells_satd.to_csv("results_sonar_codesmells_satd.csv")
sonar_not_codesmells_satd.to_csv("results_sonar_not_codesmells_satd.csv")

print(f"Sonar SATDs                 = {len(sonar_satd)}")
print(f"Sonar code_smells           = {len(sonar_codesmells)}")
print(f"Sonar code_smells&SATD      = {len(sonar_codesmells_satd)}")
print(f"SATD Detector files         = {len(satd_files)}")
print(f"code_smells&SATD/SATD files = {len(sonar_codesmells_satd)/len(satd_files)*1e2 :.4}%")
print(f"SATD + CS Mean NcLoc        = {sonar_codesmells_satd.ncloc.mean()}")
print(f"SATD + CS Mean Ciclomatic   = {sonar_codesmells_satd.ciclomatic.mean()}")
print(f"SATD + CS Mean Cognitive    = {sonar_codesmells_satd.cognitive.mean()}")
print(f"SATD + CS Mean CodeSmells   = {sonar_codesmells_satd.code_smells.mean()}")
print(f"SATD + CS Median NcLoc      = {sonar_codesmells_satd.ncloc.median()}")
print(f"SATD + CS Median Ciclomatic = {sonar_codesmells_satd.ciclomatic.median()}")
print(f"SATD + CS Median Cognitive  = {sonar_codesmells_satd.cognitive.median()}")
print(f"SATD + CS Median CodeSmells = {sonar_codesmells_satd.code_smells.median()}")
print(f"SATD - CS Mean NcLoc        = {sonar_not_codesmells_satd.ncloc.mean()}")
print(f"SATD - CS Mean Ciclomatic   = {sonar_not_codesmells_satd.ciclomatic.mean()}")
print(f"SATD - CS Mean Cognitive    = {sonar_not_codesmells_satd.cognitive.mean()}")
print(f"SATD - CS Mean CodeSmells   = {sonar_not_codesmells_satd.code_smells.mean()}")
print(f"SATD - CS Median NcLoc      = {sonar_not_codesmells_satd.ncloc.median()}")
print(f"SATD - CS Median Ciclomatic = {sonar_not_codesmells_satd.ciclomatic.median()}")
print(f"SATD - CS Median Cognitive  = {sonar_not_codesmells_satd.cognitive.median()}")
print(f"SATD - CS Median CodeSmells = {sonar_not_codesmells_satd.code_smells.median()}")
