import os
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..util import (
    get_program_root_path,
    get_db_path,
    HOSTNAME,
    PORT,
    URLComponents,
    QueryComponents,
)
from urllib.parse import urlunparse
from typing import Any


@dataclass
class AudioSourceData:
    id: str  # also the table name
    source_id: str  # used in sources= param
    media_dir: str


class AudioSource(ABC):
    """
    general table format:

    CREATE TABLE (table_name) (
        id integer PRIMARY KEY,
        expression text NOT NULL,
        reading text,
        file text NOT NULL,
        priority integer NOT NULL
    );
    """

    def __init__(self, data: AudioSourceData):
        self.data = data

    @abstractmethod
    def create_table(self):
        pass

    def init_table(self, force_init: bool):
        if force_init or not self.table_exists_and_has_data():
            print(f"(AudioSource) Initializing table: {self.data.id}")
            self.create_table()

    def execute_query(
        self, cursor: sqlite3.Connection, **params: dict[str, str]
    ) -> list[Any]:
        # - short hand is (expression = :expression AND (reading = :reading OR reading IS NULL))
        #   - expanded out statement such that the query explicit, which ensures the index is properly used
        # - order by priority is to prevent:
        #   - unnecessary post processing (best done in the query)
        #   - unnecessary unions & subqueries
        # - cannot do "expression = :expression or reading = :reading":
        #   - imagine if there existed a word in pure kana that you wanted to add, but there was
        #     a different word that had the same kana
        #   - how to prioritize without subqueries or post processing!
        # - query below is best for correctness: it is true that we can select any word that
        #   has the same reading, but there's 0 guarantee that the pitch accent will be the same!

        query = f"""
            SELECT file FROM {self.data.id} WHERE (
                (expression = :expression AND reading = :reading)
                OR (expression = :expression AND reading IS NULL)
            ) ORDER BY priority DESC
            """
        return cursor.execute(query, params).fetchall()

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
        print(parts)
        return urlunparse(parts)

    def get_sources(
        self, cursor: sqlite3.Connection, qcomp: QueryComponents
    ) -> list[dict[str, str]]:

        query_params = {
            "expression": qcomp.expression,
            "reading": qcomp.reading,
        }
        rows = self.execute_query(cursor, **query_params)

        audio_source_json_list = []
        for row in rows:
            file_path = row[0]
            name = self.get_name(row)
            url = self.construct_file_url(file_path)

            audio_source_entry = {"name": name, "url": url}
            audio_source_json_list.append(audio_source_entry)
        return audio_source_json_list

    def table_exists_and_has_data(self) -> bool:
        table_name = self.data.id

        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = :name",
                {"name": table_name},
            )
            result = cursor.fetchone()
            if int(result[0]) == 0:
                return False
            cursor.execute(f"SELECT count(*) FROM {table_name}")
            result = cursor.fetchone()
            has_data = int(result[0]) > 0
            cursor.close()
            return has_data

        return False

    def get_media_dir_path(self) -> str:
        return os.path.join(get_program_root_path(), self.data.media_dir)
