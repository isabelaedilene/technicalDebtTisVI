from csv import writer
from os import system, walk
from re import sub
from typing import List, Optional

from logzero import logger as log

from parsers import PythonParser


class Project:
    """Base class for project directory tree mapping."""

    __slots__ = ["project_root", "tree", "project_name"]

    excluded_dirs = [".idea", ".git", "venv", "__pycache__"]

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root
        if self.project_root:
            self.tree = walk(self.project_root)
            self.project_name = self.project_root.split("/").pop()

    def set_project_root(self, root_path: str):
        self.project_root = root_path
        self.tree = walk(self.project_root)
        self.project_name = self.project_root.split("/").pop()

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
        elif not file_path.endswith(".csv"):
            file_path += ".csv"
        if not self.tree:
            log.error('Please setup project root using self.set_project_root("path")')
            return
        elif self.py_files_list == []:
            log.error(
                f"Did not find any Python files in this project ({self.project_root})"
            )
            system(f"touch {file_path}")  # Adding blank CSV to avoid re-cloning and re-analyzing project
            return
        with open(file_path, "w") as c:
            csv = writer(c)
            csv.writerow(("file path", "line #", "comment", "satd"))
            for file_ in self.py_files_list:
                try:
                    py = PythonParser(file_)
                except FileNotFoundError:
                    continue
                py.get_loc()
                py.get_lo_comment()
                for com in py.hash_mark_comments:
                    com_tup = com.tuple()
                    line = com_tup[0]
                    comment = com_tup[1]
                    short_path = sub(
                        f"^{self.project_root}", self.project_name, file_
                    )
                    csv.writerow((short_path, line, comment, None))

        return file_path
