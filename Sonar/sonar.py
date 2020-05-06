from csv import writer
from logging import DEBUG, INFO
from os import chdir, getcwd
from shutil import rmtree
from subprocess import call

from git import Git
from logzero import setup_logger
from requests import get, post
from requests.auth import HTTPBasicAuth

log = setup_logger(
    name="sonar",
    level=DEBUG,
    logfile="sonar_analysis.log",
    fileLoglevel=DEBUG,
    maxBytes=1024000,
    backupCount=2,
)

BASE_PATH = "C:\\Users\\Isabela Edilene\\technicalDebtTisVI\\Sonar"  # pode ser substituído por os.getcwd()
# BASE_PATH = getcwd()


def create_sonar_project(name, url):
    log.info(f"Clonando o repositório {name}")
    Git(f"{BASE_PATH}\\Repositórios").clone(url)

    log.info(f"Criando projeto {name} no Sonar")
    chdir(f"{BASE_PATH}\\Repositórios\\{name}")
    call(
        f'sonar-scanner.bat -D"sonar.projectKey={name}" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login=dc9559a7c6abfe40fcf7fc218bd80729d4f12ed6" -D"sonar.exclusions=**/*.java"',
        shell=True,
    )


def request_sonar_components(projectKey, page):
    response = get(
        "http://localhost:9000/api/measures/component_tree",
        auth=HTTPBasicAuth(username="admin", password="admin"),
        verify=False,
        params={
            f"component": {projectKey},
            "ps": "500",
            "p": {page},
            "metricKeys": "code_smells,sqale_index,sqale_debt_ratio",
        },
    )
    responseJson = response.json()
    return responseJson


def request_sonar_delete(projectKey):
    log.debug(f"# Apagando o projeto do Sonar...")
    response = post(
        "http://localhost:9000/api/projects/delete",
        auth=HTTPBasicAuth(username="admin", password="admin"),
        verify=False,
        params={f"project": {projectKey}},
    )


def analyze_sonar_components(projectKey):
    log.info(f"Analisando projeto {projectKey}")

    # First Request
    response = request_sonar_components(projectKey, 1)
    allResults = response["components"]

    # More Requests
    totalItens = response["paging"]["total"]

    if totalItens > 500:
        neededRequests = round(totalItens / 500) + 1
        for i in range(2, neededRequests):
            response = request_sonar_components(projectKey, i)
            allResults += response["components"]

    if len(allResults) == 0:
        log.info(f"O projeto {projectKey} não retornou resultados. \n")
    else:
        with open(f"{BASE_PATH}\\analiseSonar.csv", "a") as csv_file:
            for component in allResults:
                if component["measures"][0]["value"] != "0" and (
                    ".py" in component["path"]
                ):
                    csv = writer(csv_file)
                    csv.writerow([projectKey, f'{projectKey}/{component["path"]}'])


def delete_folder(name):
    log.info(f"Apagando a pasta do computador")
    rmtree(f"{BASE_PATH}\\Repositorios\\{name}", ignore_errors=True)


def sonar_analysis():
    with open(f"{BASE_PATH}\\repositoriosPython.csv", "r", encoding="utf-8") as f:
        comments = f.read()
        for line in comments.splitlines():
            repositorio = line.replace('"', "").split(",")
            name = repositorio[0]
            url = repositorio[1]

            try:
                create_sonar_project(name, url)
                delete_folder(name)
                analyze_sonar_components(name)
                request_sonar_delete(name)
            except Exception as e:
                log.error(f"Projeto: {name} - {url} - ERRO: {e}")


if __name__ == "__main__":
    sonar_analysis()
