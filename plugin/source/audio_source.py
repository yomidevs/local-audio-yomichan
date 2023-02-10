import os
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass

from urllib.parse import urlunparse

from ..util import (
    get_program_root_path,
    HOSTNAME,
    PORT,
    URLComponents,
)


@dataclass
class AudioSourceData:
    id: str  # also the table name
    media_dir: str


class AudioSource(ABC):
    def __init__(self, data: AudioSourceData):
        self.data = data

    @abstractmethod
    def add_entries(self, connection: sqlite3.Connection):
        pass

    # def init_table(self, force_init: bool):
    #    if force_init or not self.table_exists_and_has_data():
    #        print(f"(AudioSource) Initializing table: {self.data.id}")
    #        self.create_table()

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

    # def get_sources(
    #    self, cursor: sqlite3.Connection, qcomp: QueryComponents
    # ) -> list[dict[str, str]]:

    #    query_params = {
    #        "expression": qcomp.expression,
    #        "reading": qcomp.reading,
    #    }
    #    rows = self.execute_query(cursor, **query_params)

    #    audio_source_json_list = []
    #    for row in rows:
    #        file_path = row[0]
    #        name = self.get_name(row)
    #        url = self.construct_file_url(file_path)

    #        audio_source_entry = {"name": name, "url": url}
    #        audio_source_json_list.append(audio_source_entry)
    #    return audio_source_json_list

    def get_media_dir_path(self) -> str:
        return os.path.join(get_program_root_path(), self.data.media_dir)
