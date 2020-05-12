from datetime import datetime as dt
from os import listdir, system
from shutil import rmtree
from socket import gethostname
from subprocess import Popen, PIPE
from sys import exit
from typing import List

from git import Git
from git.exc import GitCommandError
from logzero import logger as log


def notify_owner(message: str):
    # Notify code owner via local Telegram Bot script (none provided in project)
    if gethostname() == "heisenberg":
        system(f"st '{message}'")


def sys_cmd(cmd: List[str]) -> str:
    """Execute system commands using subprocess.Popen()."""

    out, err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
    # Checking return code
    if err != b"":
        log.error(err.decode())
        notify_owner(f"sys_cmd exited(1) for: {err.decode()}")
        exit(1)
    else:
        return out.decode()


def remove_directory(path: str, ans: str = "y"):
    print(f"'{path}' content: {listdir(path)}")
    while ans.lower() != "y" and ans.lower() != "n":
        ans = input(f"Remove repository local directory? [y/n] ")
    if ans.lower() == "y":
        rmtree(path)
        log.warning(f"Removed directory at '{path}'")
        return True

    return False


def clone_repository(index: int, name: str, url: str, repos_path: str) -> str:
    """Clone Git repository."""

    dt_clone = dt.now()
    try:
        Git(repos_path).clone(f"{url.replace('https', 'git')}.git")
    except GitCommandError as e:
        if "Repository not found." in str(e):
            log_msg = f"#{index} | Repository not found!"
            log.error(log_msg)
            notify_owner(log_msg)
            # raise GitCommandError
            return False
        elif "Please make sure you have the correct access rights" in str(e):
            log_msg = f"#{index} | Repository access is restricted!"
            log.error(log_msg)
            notify_owner(log_msg)
            # raise GitCommandError
            return False
        elif " already exists and is not an empty directory." in str(e):
            log.warning(f"Repository directory already exists and it's not empty.")
            if remove_directory(f"{repos_path}/{name}", "n"):
                Git(repos_path).clone(f"{url.replace('https', 'git')}.git")
            else:
                log.warning(f"Repository directory not errased. Using it as it is.")
        else:
            log.exception(f"Unindentified error! | {e}")
            notify_owner(f"#{index} | Unindentified error! | {e}")
            raise RuntimeError

    tdelta = str(dt.now() - dt_clone).split(".")[0]
    size = sys_cmd(["du", "-hs", f"{repos_path}/{name}"])
    log_msg = (
        f"#{index} | Cloned: {name} || Size: {size.split()[0]} | Timedelta: {tdelta}"
    )
    log.info(log_msg.replace("||", "|"))
    notify_owner(log_msg.replace(" || ", "\n"))

    return f"{repos_path}/{name}"


def satd_detector(comment_file: str) -> int:
    """Call satd_detector.jar to analyze comments in provided text file."""

    command = f"java -jar satd_detector/satd_detector.jar test -comment_file {comment_file} 2> /dev/null"
    exit_code = system(command)
    return exit_code
