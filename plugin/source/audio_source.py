import os
import sqlite3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final

from urllib.parse import urlunparse

from ..util import (
    get_program_root_path,
    HOSTNAME,
    PORT,
    URLComponents,
)


@dataclass
class AudioSourceData:
    id: Final[str]  # also the table name
    media_dir: Final[str]


class AudioSource(ABC):
    def __init__(self, data: AudioSourceData):
        self.data = data

    @abstractmethod
    def add_entries(self, connection: sqlite3.Connection):
        """
        add entries to the `entries` table
        """
        pass

    def get_name(self, row) -> str:
        return self.data.id

    def construct_file_url(self, file_path: str):
        """
        constructs url to get the audio file (as opposed to the url to get audio sources)
        """
        parts = URLComponents(
            scheme="http",
            netloc=f"{HOSTNAME}:{PORT}",
            path=f"{self.data.id}/{file_path}",
            params="",
            query="",
            fragment="",
        )
        return urlunparse(parts)

    def get_media_dir_path(self) -> str:
        return os.path.join(get_program_root_path(), self.data.media_dir)
