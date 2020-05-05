import os
import git
import time
import shutil
import requests
import subprocess
from csv import writer
from json import dumps
from requests.auth import HTTPBasicAuth

BASE_PATH = "C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar"

def createSonarProject(name, url): 
	print(f"INFO: Clonando o repositório {name}")
	git.Git(f"{BASE_PATH}\\Reositorios").clone(url)

	print(f"INFO: Criando projeto {name} no Sonar")
	os.chdir(f"{BASE_PATH}\\Repositorios\\{name}") 
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
	print(f"INFO: Analisando projeto {projectKey}")

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

	if(len(allResults) == 0):
		log(f"O projeto {projectKey} não retornou resultados. \n")
	else:
		with open(f'{BASE_PATH}\\analiseSonar.csv','a') as csv_file:
			for component in allResults:
				if component["measures"][0]["value"] != "0" and (".py" in component["path"]):
					csv = writer(csv_file)  
					csv.writerow([projectKey, f'{projectKey}/{component["path"]}'])

def deleteFolder(name):
	print("INFO: Apagando a pasta do computador")
	shutil.rmtree(f"{BASE_PATH}\\Repositorios\\{name}", ignore_errors=True)

def log(msg):
	with open(f"{BASE_PATH}\\log.txt", "a", encoding="utf-8") as arquivo:
		arquivo.write(msg)

def sonarAnalysis():
	with open(f"{BASE_PATH}\\repositoriosPython.csv", "r", encoding="utf-8") as f:
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
				log(f"Projeto: {name} - {url} - ERRO: {e} \n")

sonarAnalysis()






