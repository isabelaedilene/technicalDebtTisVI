import tokenize
from io import BytesIO
from logging import DEBUG, INFO, WARNING
from os.path import exists
from re import match
from typing import Optional

from logzero import setup_logger

log = setup_logger(level=WARNING)


class LanguageParser:
    """Base class for finding comments in programming languages."""

    __slots__ = ["src_file_string", "src_file_path", "loc", "lo_comment"]

    def __init__(
            self,
            src_file_path: Optional[str] = None,
            src_file_string: Optional[str] = None,
    ):
        self.src_file_string = src_file_string
        if src_file_path:
            self.load_src_file(src_file_path)

    def check_loaded_string(self) -> bool:
        """Checks if source file is already loaded before executing methods."""
        if self.src_file_string == None or not type(self.src_file_string) is str:
            log.error(
                f"Source file was not loaded yet. "
                f"Load it using load_src_file() method."
            )
            raise UnboundLocalError
        else:
            return True

    def get_loc(self) -> int:
        """Return LoC for current source file."""
        self.check_loaded_string()
        loc = 0
        for line in self.src_file_string.splitlines():
            if not match("^[\s]*$", line):
                loc += 1
        log.info(f"LoC: {loc}")
        self.loc = loc
        return loc

    def load_src_file(self, file_path: str, file_encoding: str = "utf-8"):
        """Loads programming language source file."""
        if not exists(file_path):
            log.error(f"Source file not found at provided path ({file_path})")
            raise FileNotFoundError
        with open(file_path, "r", encoding=file_encoding) as src_file:
            self.src_file_string = src_file.read()
        self.src_file_path = file_path
        log.info(f"Loaded source file ({file_path})")


class PythonParser(LanguageParser):
    """Python language comment parser class."""

    __slots__ = ["hash_mark_comments"]


    def __init__(
            self,
            src_file_path: Optional[str] = None,
            src_file_string: Optional[str] = None,
    ):
        super().__init__(
            src_file_path=src_file_path,
            src_file_string=src_file_string
        )
        self.hash_mark_comments = []

    class HashMark:
        """Hash mark comment instance."""

        __slots__ = ["line_number", "comment_string", "line_string"]

        def __init__(
                self,
                line_number: int,
                comment_string: str,
                line_string: str,
        ):
            self.line_number = line_number
            self.comment_string = comment_string.strip("#").strip()
            self.line_string = line_string

        def tuple(self):
            return (self.line_number, self.comment_string, self.line_string)

        def __repr__(self):
            return (
                f"<HashMark("
                f"line_number={self.line_number}; "
                f'comment_string="{self.comment_string}"; '
                f'line_string="{self.line_string}";'
                f")>"
            )

        def __str__(self):
            return (
                f"line number: {self.line_number} "
                f"| comment string: {self.comment_string.strip()} "
                f"| line string: {self.line_string.strip()}"
            )

    class TripleQuotes:  # TODO
        """Tripe quotes (single/double) docstring instance."""

        __slots__ = [
            "start_line",
            "end_line",
            "start_column",
            "end_column",
            "type",
            "string",
        ]

        def __init__(
            self,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
            start_column: Optional[int] = None,
            end_column: Optional[int] = None,
            quote_type: Optional[str] = None,
            string: Optional[str] = None,
        ):
            self.start_line = start_line
            self.end_line = end_line
            self.start_column = start_column
            self.end_column = end_column
            self.type = quote_type
            self.string = string

        def set_start_line(self, start_line: int):
            self.start_line = start_line

        def set_end_line(self, end_line: int):
            self.end_line = end_line

        def set_start_column(self, start_column: int):
            self.start_column = start_column

        def set_end_column(self, end_column: int):
            self.end_column = end_column

    def find_docstring_comments(self):  # TODO
        """Find docstring comments."""
        self.check_loaded_string()
        docstring_comment_list = []
        tokenized = tokenize.tokenize(
            BytesIO(self.src_file_string.encode()).readline
        )
        for t_type, t_string, t_xy_start, t_xy_end, line in tokenized:
            if t_type is tokenize.STRING:
                tmp_token = tokenize.tokenize(
                    BytesIO(line.encode()).readline
                )

    def get_lo_comment(self) -> int:
        """Return lines of comment for current source file."""
        self.check_loaded_string()
        lo_comment = 0
        tokenized = tokenize.tokenize(
            BytesIO(self.src_file_string.encode()).readline
        )
        for t_type, t_string, t_xy_start, t_xy_end, line in tokenized:
            if t_type is tokenize.COMMENT:
                lo_comment += 1
                self.hash_mark_comments.append(
                    self.HashMark(t_xy_start[0], t_string, line)
                )
        log.info(f"Lines of comment: {lo_comment}")
        self.lo_comment = lo_comment
        return lo_comment
