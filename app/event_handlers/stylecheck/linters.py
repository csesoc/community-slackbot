from pylint import epylint as lint
import subprocess
from subprocess import PIPE, STDOUT


def run_c_lint(code_entry):
    """
    :param code_entry:
    :return: Lint Result
    """
    process = subprocess.Popen(f"cpplint {code_entry.file_path}", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = process.stdout.read().decode("utf-8")
    return "Failed: C Lint" if output is None else output


def run_py_lint(code_entry):
    """
    :param code_entry:
    :return: Lint Result
    """
    (stdout, stderr) = lint.py_run(code_entry.file_path, return_std=True)
    return stdout.read()