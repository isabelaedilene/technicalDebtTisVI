from getopt import getopt, GetoptError
from os import walk
from os.path import basename
from sys import argv, exit
from typing import List, Optional

from parsers import PythonParser

usage = (
    f"Syntax:\n"
    f"\n{basename(__file__)} -f <file_path>"
    f"\nOR"
    f"\n{basename(__file__)} -p <project_root_path>"
    f"\n\nArguments:"
    f"\n\t-f  --file=\t\tPath to file"
    f"\n\t-p  --project=\t\tPath to project's root"
)


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

    def is_not_excluded_dir(self, dir_path: str, excluded_list: Optional[List[str]] = None):
        if excluded_list == None:
            excluded_list = self.excluded_dirs
        if dir_path[len(self.project_root)+1:].split("/")[0] in excluded_list:
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


def analyze_file(file_path: str):
    py = PythonParser(file_path)
    print(f"File: {file_path}")
    print(f"LoC:      {py.get_loc()}")
    print(f"Comments: {py.get_lo_comment()}")
    if py.lo_comment > 0:
        print(f"Comments found:")
        [print(comment.tuple()) for comment in py.hash_mark_comments]


def analyze_project(project_path: str):
    py = Python(project_path)
    print(f"Project analysis:")
    [analyze_file(f) for f in py.py_files_list]



def main(argv):
    file_path = None
    project_path = None
    # Parsing arguments
    try:
        opts, args = getopt(argv, "hp:f:", ["help", "project=", "file="])
    except GetoptError:
        print(usage)
        exit(3)
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(usage)
                exit(3)
            elif opt in ("-p", "--project"):
                project_path = arg
            elif opt in ("-f", "--file"):
                file_path = arg
    if file_path:
        analyze_file(file_path)
    elif project_path:
        analyze_project(project_path)
    else:
        print(usage)
        exit(3)


if __name__ == "__main__":
    main(argv[1:])
