# Python comment parser

## What does it do
Reads Python files and return file LoC, number of comment lines, comment strings
and identifies self-admitted technical debts (SATD) in them.

## Requirements
```
Python    >= 3.6
GitPython == 3.1.1
logzero   == 1.5.0
pandas    == 1.0.3
requests  == 2.23.0
```

## Setup
`pip3 install -r requirements.txt`

## Usage
`python3 project-parser.py -f <file_path>`

or

`python3 project-parser.py -p <project_path> [-c <0|1>]`
