from csv import writer
from requests import get, post
from requests.auth import HTTPBasicAuth


def requestSonarComponents(projectKey, page):
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


def requestSonarDelete(projectKey):
    response = post(
        "http://localhost:9000/api/projects/delete",
        auth=HTTPBasicAuth(username="admin", password="admin"),
        verify=False,
        params={f"project": {projectKey}},
    )


with open("analiseSonar.csv", "w") as csv_file:
    csv = writer(csv_file)
    csv.writerow(
        ("project name", "code smells", "sqale index", "sqale debt ratio", "file path")
    )


for projectKey in projects:
    print(f"Analisando {projectKey}...")

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

    # print(dumps(allResults, indent=4, sort_keys=True))

    # Write CSV
    for component in allResults:
        if component["measures"][0]["value"] != "0" and (".py" in component["path"]):
            try:
                with open("analiseSonar.csv", "a") as csv_file:
                    csv = writer(csv_file)
                    csv.writerow(
                        [
                            projectKey,
                            component["measures"][0]["value"],
                            component["measures"][1]["value"],
                            component["measures"][2]["value"],
                            component["path"],
                        ]
                    )
            except Exception as e:
                print(f"ERRO: {e}")

    # Delete project
    requestSonarDelete(projectKey)