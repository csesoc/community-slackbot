from pylint import epylint as lint

def run_c_lint():
    pass


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
