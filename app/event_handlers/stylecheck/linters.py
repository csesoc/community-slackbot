import shlex
from pylint import epylint as lint
import subprocess
from subprocess import PIPE, STDOUT


def run_c_lint(code_entry):
    """
    :param code_entry:
    :return: Lint Result
    """
    cmd = shlex.split("cpplint {}".format(code_entry.file_path))
    process = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = process.stdout.read()
    return "Failed: C Lint" if output is None else output


def run_py_lint(code_entry):
    """
    :param code_entry:
    :return: Lint Result
    """
    (stdout, stderr) = lint.py_run(code_entry.file_path, return_std=True)

    print("<<Result>>")
    print(code_entry.code)
    print("<<Result>>")

    return stdout.read()