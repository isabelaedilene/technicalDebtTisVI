from csv import writer
from os import listdir
from os.path import exists

import pandas as pd

from logzero import logger as log

satd_repos = "satd_repos.csv"


def target_csv(csv: str) -> bool:
    try:
        df = pd.read_csv(csv)
    except pd.errors.EmptyDataError:
        return False
    # log.debug(f"lines: {len(df)}")
    for item in df["satd"]:
        if item == "SATD":
            return True
    return False


def register_repo(repo: str):
    if not exists(satd_repos):
        with open(satd_repos, "w") as c:
            csv = writer(c)
            csv.writerow(("project", "url"))
    df = pd.read_csv("python_repos.csv")
    found = df[df.name == repo]["url"].to_list()
    if len(found) > 1:
        log.warning(found)
    elif len(found) == 1:
        with open(satd_repos, "a") as c:
            csv = writer(c)
            csv.writerow((repo, found[0]))
        log.info(f"Added: {repo}")
    else:
        log.debug(f"Clean: {repo}")


def skip(repo: str) -> bool:
    if not exists(satd_repos):
        return False
    with open(satd_repos, "r") as c:
        if repo in c.read():
            return True
    return False


def main():
    for i, file_ in enumerate(listdir("tmp")):
        if file_.endswith(".csv"):
            if target_csv(f"tmp/{file_}") and not skip(file_.replace(".csv", "")):
                log.warning(f"#{i}\tSATD in {file_}")
                register_repo(file_.replace(".csv", ""))
            else:
                log.info(f"#{i}\tClean project")


if __name__ == "__main__":
    main()
