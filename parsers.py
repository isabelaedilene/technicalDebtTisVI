from os.path import exists
from re import match
from typing import Optional

from logzero import logger as log


class Language:
    """Base class for programming languages."""
    __slots__ = ["src_str"]

    def __init__(self):
        self.src_str: Optional[str] = None

    def check_loaded_file(self) -> bool:
        """Checks if source file is already loaded before executing methods."""
        if self.src_str == None or not self.src_str is str:
            log.error(
                f"Source file was not loaded yet. "
                f"Load it using load_src_file() method."
            )
            raise UnboundLocalError
        else:
            return True

    def get_loc(self) -> int:
        """Return LoC for current source file."""
        self.check_loaded_file()
        loc: int = 0
        for line in self.src_str.splitlines():
            if not match("^\s*$", line):
                loc += 1
        log.info(f"LoC: {loc}")
        return loc

    def load_src_file(self, file_path: str, file_encoding: str = "utf-8"):
        """Loads programming language source file."""
        if not exists(file_path):
            log.error(f"Source file not found at provided path ({file_path})")
            raise FileNotFoundError
        with open(file_path, "r", encoding=file_encoding) as src_file:
            self.src_str = src_file.read()
        log.debug(f"Loaded source file ({file_path})")


class Python(Language):
    """Python language parser class."""
    __slots__ = []

    class TripleQuotes:
        """Instantiate an object to identify and isolate triple quotes comments."""
        __slots__ = ["start_line", "end_line", "start_column", "end_column"]
        def __init__(self, start_line: Optional[int] = None):
            self.start_line: Optional[int] = start_line
            self.end_line: Optional[int] = None
            self.start_column: Optional[int] = None
            self.end_column: Optional[int] = None

        def set_start_line(self, start_line: int):
            self.start_line: int = start_line

        def set_end_line(self, end_line: int):
            self.end_line: int = end_line

        def set_start_column(self, start_column: int):
            self.start_column: int = start_column

        def set_end_column(self, end_column: int):
            self.end_column: int = end_column

    def find_hash_mark_comments(self):
        """Find all hash mark comments."""
        self.check_loaded_file()
        comment_list = []
        for i, line in enumerate(self.src_str.splitlines()):
            if "#" in line:
                log.debug(f"Found # on line #{i}: {line}")
                comment_list.append((i, line))
                if i - 1 >= 0:
                    pass

