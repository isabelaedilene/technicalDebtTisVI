from csv import writer
from datetime import datetime as dt
from logging import DEBUG, INFO
from os import getcwd, listdir, makedirs
from os.path import exists
from shutil import rmtree

import pandas as pd
from logzero import setup_logger

from models import Python
from tools import clone_repository, notify_owner, satd_detector

log = setup_logger(
    name="app",
    level=DEBUG,
    logfile="satd_detector.log",
    fileLoglevel=DEBUG,
    maxBytes=1024000,
    backupCount=2,
)

# Making temporary directory to store cloned repositories and comment CSVs
repos_path = "/tmp/repositories"
if not exists(repos_path):
    makedirs(repos_path)
comment_path = f"{getcwd()}/comments"
if not exists(comment_path):
    makedirs(comment_path)


def get_comments(index: int, name: str, repo_path: str = repos_path):
    # Analyzing comments in each repository
    dt_satd = dt.now()
    py_project = Python(f"{repo_path}/{name}")
    py_project.export_csv(f"{comment_path}/{name}.csv")
    tdelta = str(dt.now() - dt_satd).split('.')[0]

    log_msg = f"#{index}\t | Analyzed: {name} | Timedelta: {tdelta}"
    log.info(log_msg)
    notify_owner(log_msg)
    rmtree(f"{repo_path}/{name}")
    log.info(f"Removed repository directory ({repo_path}/{name})")

    return True


# Cloning repositories and getting its comments
df = pd.read_csv("python_repositories.csv")
for i, repo in enumerate(zip(df["name"], df["url"])):
    repo_name = repo[0]
    if f"{repo_name}.csv" in listdir(comment_path):
        log.debug(f"Skipping {repo_name}. Already cloned and indexed.")
        continue
    repo_url = repo[1]
    log.info(f"#{i}\t | Project: {repo_name}")
    project_path = clone_repository(i, repo_name, repo_url, repos_path)
    get_comments(i, repo_name)
log.info("Done cloning repositories and indexing comments")

# Detecting SATDs in comments
with open(f"{getcwd()}/ALL_comments.csv", "w") as f:
    csv_w = writer(f)
    csv_w.writerow(("project name", "file path", "line #", "comment", "satd"))
    for i, csv in enumerate(listdir(comment_path)):
        log.info(f"#{i}\t | SATD detection on project: {csv.strip('.csv')}")
        df = pd.read_csv(f"{comment_path}/{csv}")
        for comment in df["comment"]:
            satd = satd_detector(comment)
            csv_w.writerow(
                (
                    csv.strip(".csv"),
                    df["file path"],
                    df["line #"],
                    df["comment"],
                    satd
                )
            )
log.info("Finished everything.")
