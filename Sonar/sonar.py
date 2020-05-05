import os
import git
import time
import shutil
import requests
import subprocess
from csv import writer
from json import dumps
from requests.auth import HTTPBasicAuth

BASE_PATH = "C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar\\Repositorios"

def createSonarProject(name, url): 
	print(f"# Clonando o repositório {name}...")
	git.Git(BASE_PATH).clone(url)

	print(f"# Criando projeto no SonarQube...")
	os.chdir(f"{BASE_PATH}\\{name}") 
	subprocess.call(f'sonar-scanner.bat -D"sonar.projectKey={name}" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login=dc9559a7c6abfe40fcf7fc218bd80729d4f12ed6" -D"sonar.exclusions=**/*.java"', shell= True)

def requestSonarComponents(projectKey, page):
	response = requests.get(
	            'http://localhost:9000/api/measures/component_tree',
	            auth   = HTTPBasicAuth(username="admin", password="admin"),
	            verify = False,
	            params = {f'component': {projectKey}, 'ps' :'500', 'p' :{page}, 'metricKeys': 'code_smells,sqale_index,sqale_debt_ratio'})
	responseJson = response.json()
	return responseJson

def requestSonarDelete(projectKey):
	print("# Apagando o projeto do Sonar...")
	response = requests.post(
	            'http://localhost:9000/api/projects/delete',
	            auth   = HTTPBasicAuth(username="admin", password="admin"),
	            verify = False,
	            params = {f'project' : {projectKey}})

def analyzeSonarComponents(projectKey):
	print(f"# ANALISANDO O PROJETO {projectKey}...")

	# First Request
	response = requestSonarComponents(projectKey, 1)
	allResults = response["components"]

	# More Requests
	totalItens = response["paging"]["total"]

	if totalItens > 500:
		neededRequests = round(totalItens / 500) + 1
		for i in range(2, neededRequests):
			response = requestSonarComponents(projectKey, i)
			allResults += response["components"]

	with open('C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar\\analiseSonar.csv','a') as csv_file:
		for component in allResults:
			if component["measures"][0]["value"] != "0" and (".py" in component["path"]):
				csv = writer(csv_file)  
				csv.writerow([projectKey, component["measures"][0]["value"], component["measures"][1]["value"], component["measures"][2]["value"], component["path"] ])

def deleteFolder(name):
	print("# Apagando a pasta do computador...")
	shutil.rmtree(f"{BASE_PATH}\\{name}", ignore_errors=True)

def sonarAnalysis():
	with open("C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar\\repositoriosPython.csv", "r", encoding="utf-8") as f:
		comments = f.read()
		for line in comments.splitlines():
			repositorio = line.replace('"', '').split(',')
			name = repositorio[0]
			url = repositorio[1]

			try:
				createSonarProject(name, url)
				deleteFolder(name)
				analyzeSonarComponents(name)
				requestSonarDelete(name)	
			except Exception as e: 
				with open("C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar\\log.csv", "a", encoding="utf-8") as csv_file:
					csv = writer(csv_file)  
					csv.writerow(f"Não foi possível analisar o projeto {name}, {url}. ERRO: {e}")

sonarAnalysis()






