from os import getcwd
from unittest import main, TestCase

from logzero import logger as log

from parsers import PythonParser


class TestPythonParser(TestCase):
    src_file = "parsers.py"
    cwd = "/Users/tulio/devel/python/puc/comment-parser"

    def test_cwd(self):
        self.assertEqual(self.cwd, getcwd())

    def test_check_loaded_string_exception(self):
        py = PythonParser()
        with self.assertRaises(UnboundLocalError):
            py.check_loaded_string()

    def test_load_src_file(self):
        py = PythonParser()
        py.load_src_file(self.src_file)
        self.assertEqual(self.src_file, py.src_file_path)

    def test_check_loaded_string(self):
        py = PythonParser()
        py.load_src_file(self.src_file)
        self.assertEqual(True, py.check_loaded_string())

    def test_get_loc(self):
        py = PythonParser()
        py.load_src_file(self.src_file)
        self.assertEqual(128, py.get_loc())

    def test_get_lo_comments(self):
        py = PythonParser()
        py.load_src_file(self.src_file)
        self.assertEqual(2, py.get_lo_comment())


if __name__ == "__main__":
    main()
