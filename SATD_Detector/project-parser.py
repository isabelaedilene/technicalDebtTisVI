from csv import writer
from getopt import getopt, GetoptError
from logging import DEBUG, INFO, WARNING
from os import system, walk
from os.path import basename
from sys import argv, exit
from typing import List, Optional

from logzero import setup_logger

from parsers import PythonParser

log = setup_logger(name="project-parser", level=DEBUG)

usage = (
    f"Syntax:\n"
    f"\n{basename(__file__)} -f <file_path>"
    f"\nOR"
    f"\n{basename(__file__)} -p <project_root_path> [-c <0|1>]"
    f"\n\nArguments:"
    f"\n\t-f  --file=\t\tPath to file"
    f"\n\t-p  --project=\t\tPath to project's root"
    f"\n\t-c  --csv=\t\t\t0=False/1=True To save analysis to CSV file (default=0)"
)


def satd_detector(comment: str) -> bool:
    """Execute system commands using subprocess.Popen()."""

    command = (
        f"[[ ! $("
        f"echo '{comment}' | java -jar satd_detector.jar test 2>/dev/null"
        f") =~ .*Not.* ]] && exit 2 || exit 1"
    )
    exit_code = system(command)
    if exit_code == 512:
        log.debug(f"SATD\t | {comment}")
        return True
    elif exit_code == 256:
        log.debug(f"Not SATD\t | {comment}")
        return False
    else:
        log.error(f"IDK! exit={exit_code}")
        raise RuntimeError


class Project:
    """Base class for project directory tree mapping."""

    __slots__ = ["project_root", "tree"]

    excluded_dirs = [".idea", ".git", "venv", "__pycache__"]

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root
        if self.project_root:
            self.tree = walk(self.project_root)

    def set_project_root(self, root_path: str):
        self.project_root = root_path
        self.tree = walk(self.project_root)

    def is_not_excluded_dir(
        self, dir_path: str, excluded_list: Optional[List[str]] = None
    ):
        if excluded_list == None:
            excluded_list = self.excluded_dirs
        if dir_path[len(self.project_root) + 1 :].split("/")[0] in excluded_list:
            return False
        return True


class Python(Project):
    """Class for PythonParser project directory and .py files tree mapping."""

    __slots__ = ["py_files_list"]

    def __init__(self, project_path: Optional[str] = None):
        self.py_files_list = []
        self.tree = None
        super().__init__(project_path)
        if self.tree:
            for path, dirs, files in self.tree:
                if self.is_not_excluded_dir(path):
                    for file_ in files:
                        if file_.endswith(".py"):
                            self.py_files_list.append(f"{path}/{file_}")

    def export_csv(self, file_path: Optional[str] = None):
        if file_path == None:
            file_path = f"{self.project_root}/comments.csv"
        if not self.tree:
            log.error('Please setup project root using self.set_project_root("path")')
            return
        elif self.py_files_list == []:
            log.error(
                f"Did not find any Python files in this project ({self.project_root})"
            )
            return
        with open(file_path, "w") as c:
            csv = writer(c)
            csv.writerow(("file path", "line #", "comment", "satd"))
        for file_path in self.py_files_list:
            py = PythonParser(file_path)
            py.get_loc()
            py.get_lo_comment()
            with open(file_path, "a") as c:
                csv = writer(c)
                for com in py.hash_mark_comments:
                    com_tup = com.tuple()
                    line = com_tup[0]
                    comment = com_tup[1]
                    satd = satd_detector(comment)
                    csv.writerow((file_path, line, comment, satd))


def analyze_file(file_path: str):
    py_file = PythonParser(file_path)
    print(f"File: {file_path}")
    print(f"LoC:      {py_file.get_loc()}")
    print(f"Comments: {py_file.get_lo_comment()}")
    if py_file.lo_comment > 0:
        print(f"Comments found:")
        [print(comment.tuple()) for comment in py_file.hash_mark_comments]


def analyze_project(project_path: str):
    py_project = Python(project_path)
    print(f"Project analysis:")
    [analyze_file(f) for f in py_project.py_files_list]


def main(argv):
    file_path = None
    project_path = None
    csvfy = False
    # Parsing arguments
    try:
        opts, args = getopt(argv, "hf:p:c:", ["help", "file=", "project=", "csv="])
    except GetoptError:
        print(usage)
        exit(3)
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(usage)
                exit(3)
            elif opt in ("-f", "--file"):
                file_path = arg
            elif opt in ("-p", "--project"):
                project_path = arg
            elif opt in ("-c", "--csv"):
                csvfy = arg
    if file_path:
        analyze_file(file_path)
    elif project_path:
        if not csvfy:
            analyze_project(project_path)
        else:
            py_project = Python(project_path)
            csv_file = py_project.export_csv()
            if csv_file:
                log.info(f"Exported CSV file to {py_project.project_root}/{csv_file}")
    else:
        print(usage)
        exit(3)


if __name__ == "__main__":
    main(argv[1:])
