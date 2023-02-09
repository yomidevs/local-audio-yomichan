import os
from typing import NamedTuple
from dataclasses import dataclass

HOSTNAME = "localhost"
PORT = 5050
DB_FILE_NAME = "entries.db"

def is_kana(word):
    for char in word:
        if char < 'ぁ' or char > 'ヾ':
            return False
    return True

def get_program_root_path():
    return os.path.dirname(os.path.realpath(__file__)).replace("\\", "/").removesuffix("/")

def get_db_path():
    return os.path.join(get_program_root_path(), DB_FILE_NAME)

class URLComponents(NamedTuple):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

@dataclass(frozen=True)
class QueryComponents():
    expression: str
    reading: str
    sources: list[str]
    user: list[str]

AudioSourceJsonEntry = dict[str, str]
AudioSourceJsonList = list[AudioSourceJsonEntry]
