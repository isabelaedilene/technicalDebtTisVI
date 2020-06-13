import os
import git
import time
import shutil
import requests
import subprocess
from csv import writer
from json import dumps
from requests.auth import HTTPBasicAuth

BASE_PATH = "C:\\Users\\Isabela Edilene\\GitHub\\technicalDebtTisVI\\Sonar"

def createSonarProject(name, url): 
	print(f"INFO: Clonando o repositório {name}")
	git.Git(f"{BASE_PATH}\\Repositorios").clone(url)

	print(f"INFO: Criando projeto {name} no Sonar")
	os.chdir(f"{BASE_PATH}\\Repositorios\\{name}") 
	subprocess.call(f'sonar-scanner.bat -D"sonar.projectKey={name}" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login=dc9559a7c6abfe40fcf7fc218bd80729d4f12ed6" -D"sonar.exclusions=**/*.java, **/*.js"', shell= True)

def requestSonarComponents(projectKey, page):
	response = requests.get(
	            'http://localhost:9000/api/measures/component_tree',
	            auth   = HTTPBasicAuth(username="admin", password="admin"),
	            verify = False,
	            params = {f'component': {projectKey}, 'ps' :'500', 'p' :{page}, 'metricKeys': 'ncloc,complexity,cognitive_complexity,code_smells'})
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
		for i in range(2, neededRequests + 1):
			response = requestSonarComponents(projectKey, i)
			allResults += response["components"]

	msg = f"O PROJETO {projectKey} ESTÁ VAZIO"
	if(len(allResults) == 0):
		log(msg)
	else:
		with open(f'{BASE_PATH}\\analiseSonar.csv','a', newline = '', encoding="utf-8") as csv_file:
			for component in allResults:				
				if component["qualifier"] == "FIL" and component["language"] == "py" and len(component["measures"]) > 3:
					csv = writer(csv_file)  
					csv.writerow(
								[projectKey,
								f'{projectKey}/{component["path"]}',
								component["measures"][0]["value"],
								component["measures"][1]["value"], 
								component["measures"][2]["value"] if component["measures"][2]["metric"] == "cognitive_complexity" else component["measures"][3]["value"],
								component["measures"][3]["value"] if component["measures"][3]["metric"] == "code_smells" else component["measures"][2]["value"],
					])

def deleteFolder(name):
	print("INFO: Apagando a pasta do computador")
	shutil.rmtree(f"{BASE_PATH}\\Repositorios\\{name}", ignore_errors=True)

def log(msg):
	with open(f"{BASE_PATH}\\log.txt", "a", encoding="utf-8") as arquivo:
		arquivo.write(msg)

def sonarAnalysis():
	cont = 0
	# analyzeSonarComponents("")
	with open(f"{BASE_PATH}\\repositoriosPython.csv", "r", encoding="utf-8") as f:
		comments = f.read()
		for line in comments.splitlines():
			cont = cont + 1
			print(f"ANALISANDO O PROJETO #{cont}")

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






