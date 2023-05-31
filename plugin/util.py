import os
from typing import NamedTuple
from dataclasses import dataclass

from .consts import DB_FILE_NAME, ANDROID_DB_FILE_NAME



def get_program_root_path():
    return (
        os.path.dirname(os.path.realpath(__file__)).replace("\\", "/").removesuffix("/")
    )


def get_db_path():
    return os.path.join(get_program_root_path(), DB_FILE_NAME)


def get_android_db_path():
    return os.path.join(get_program_root_path(), ANDROID_DB_FILE_NAME)


class URLComponents(NamedTuple):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str


@dataclass(frozen=True)
class QueryComponents:
    expression: str
    reading: str
    sources: list[str]
    user: list[str]


AudioSourceJsonEntry = dict[str, str]
AudioSourceJsonList = list[AudioSourceJsonEntry]

