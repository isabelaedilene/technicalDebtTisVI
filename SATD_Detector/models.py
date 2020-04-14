from csv import writer
from os import walk
from typing import List, Optional

from logzero import logger as log

from parsers import PythonParser
from tools import satd_detector


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

        return file_path
