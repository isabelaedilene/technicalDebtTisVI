from getopt import getopt, GetoptError
from logging import DEBUG, INFO, WARNING
from os.path import basename
from sys import argv, exit

from logzero import setup_logger

from models import Python
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
