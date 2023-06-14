from pathlib import Path
from typing import NamedTuple, Optional
from dataclasses import dataclass

from .consts import DB_FILE_NAME, ANDROID_DB_FILE_NAME



def get_program_root_path():
    """
    gets 'plugin' folder in repo, or the add-on ID on AnkiWeb
    """
    return (
        Path(__file__).parent
    )


def get_db_path():
    return get_program_root_path().joinpath(DB_FILE_NAME)


def get_android_db_path():
    return get_program_root_path().joinpath(ANDROID_DB_FILE_NAME)


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
    reading: Optional[str]
    sources: list[str]
    user: list[str]


AudioSourceJsonEntry = dict[str, str]
AudioSourceJsonList = list[AudioSourceJsonEntry]

