import sqlite3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from urllib.parse import urlunparse

from ..util import (
    get_data_dir,
    URLComponents,
)
from ..consts import (
    HOSTNAME,
    PORT,
)


@dataclass
class AudioSourceData:
    id: Final[str]  # also the table name
    media_dir: Final[str]
    display: Final[str]


class AudioSource(ABC):
    def __init__(self, data: AudioSourceData):
        self.data = data

    @abstractmethod
    def add_entries(self, connection: sqlite3.Connection):
        """
        add entries to the `entries` table
        """
        pass

    def is_supported_audio_file_ext(self, path):
        """
        determine whether a given file path is a valid audio file extension
        """
        if not isinstance(path, Path):
            path = Path(path)
        if not path.is_file():
            return False
        # audio container formats supposedly supported by browsers (excluding webm since it's typically for videos)
        if not path.suffix.lower() in ['.mp3', '.m4a', '.aac', '.ogg', '.oga', '.opus', '.flac', '.wav']:
            print(f"({self.__class__.__name__}) skipping non-audio file: {path}")
            return False
        return True

    def find_media_files(self):
        """
        returns a list of all valid audio files in the media_dir
        """
        return filter(self.is_supported_audio_file_ext, self.get_media_dir_path().rglob("*"))

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

    def get_media_dir_path(self) -> Path:
        return get_data_dir().joinpath(self.data.media_dir)
