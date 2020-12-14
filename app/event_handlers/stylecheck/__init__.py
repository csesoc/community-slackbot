"""
If file contains a http site make sure you add the oauth scope file:read to the bot
"""

import os
import uuid
from guesslang import Guess
import requests
from app.event_handlers.stylecheck.linters import *

FILE_FOLDER = "./temp_files"
if not os.path.exists(FILE_FOLDER):
    os.mkdir(FILE_FOLDER)

SUPPORTED_LANGUAGES = [
    "C", "C++", "Python"
]

SUPPORTED_FILE_TYPES = [
    "c", "cpp", "py"
]

TYPE_TO_LANGUAGE_MAPPING = dict(zip(SUPPORTED_FILE_TYPES, SUPPORTED_LANGUAGES))
LANGUAGE_TO_TYPE_MAPPING = dict(zip(SUPPORTED_LANGUAGES, SUPPORTED_FILE_TYPES))
language_guess = Guess()


class CodeEntry:
    def __init__(self, language, code, file_path):
        self.language = language
        self.code = code
        self.file_path = file_path

    def run_linting(self):
        """
        :return: Linting Result
        """
        if self.language in SUPPORTED_LANGUAGES[:2]:
            return run_c_lint(self)
        elif self.language == SUPPORTED_LANGUAGES[2]:
            return run_py_lint(self)

        return 'No Linting Run: ' + self.language


def recognise_language(file_path: str = None, code: str = None) -> str:
    """
    :param file_path:
    :param code:
    :return: Programming Language
    """
    language = None
    if code is None and file_path is not None:
        language = TYPE_TO_LANGUAGE_MAPPING.get(file_path.split(".")[-1].lower(), None)
    elif code is not None and file_path is None:
        language = language_guess.language_name(code)
    return language if (language in SUPPORTED_LANGUAGES) else None


def get_code_from_file(file_path) -> str:
    with open(file_path, "r") as f:
        return f.read()


def get_code_from_text(text) -> str:
    return text[len("stylecheck"):]


def save_code_file(slack_token, url: str = None, code: str = None, language: str = None) -> str:
    file_path = None
    if url is not None:
        res = requests.get(url, headers={'Authorization': 'Bearer' + ' ' + slack_token}, allow_redirects=True)
        terms = url.split('/')
        file_path = os.path.join(FILE_FOLDER, terms[-1])
        with open(file_path, 'wb') as f:
            f.write(res.content)
    elif code is not None:
        file_name = str(uuid.uuid4()) + "." + LANGUAGE_TO_TYPE_MAPPING[language]
        file_path = os.path.join(FILE_FOLDER, file_name)
        with (open(file_path, "w")) as f:
            f.write(code)
    return file_path


def handle_style_check_request(client, slack_token, event_data):
    event = event_data['event']
    channel = event_data["event"]["channel"]
    language = None
    code_entry = None
    if 'files' in event:
        # Attempt to get code from file
        file_url = event_data['event']['files'][0]['url_private_download']
        file_path = save_code_file(slack_token, url=file_url)
        language = recognise_language(file_path=file_path)
        if language is not None:
            code_entry = CodeEntry(language, get_code_from_file(file_path), file_path)
    else:
        # Attempt to get code from message
        code = get_code_from_text(event_data['event']['text'])
        language = recognise_language(code=code)
        if language is not None:
            file_path = save_code_file(slack_token, code=code, language=language)
            code_entry = CodeEntry(language, code, file_path)
    if code_entry is not None:
        lint_result = code_entry.run_linting()
        message = "Linting Result:\n" + lint_result
        client.chat_postMessage(channel=channel, text=message)
    else:
        message = 'Unable to process your code :unamused:'
        client.chat_postMessage(channel=channel, text=message)