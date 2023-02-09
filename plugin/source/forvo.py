import os
import sqlite3

from .audio_source import AudioSource, AudioSourceData
from ..util import get_db_path, QueryComponents, AudioSourceJsonEntry, AudioSourceJsonList

class ForvoAudioSource(AudioSource):
    def create_table(self):
        start = self.data.media_dir

        drop_table_sql = "DROP TABLE IF EXISTS forvo"
        # no concept of priority here because there is nothing to prioritize (no reading)
        create_table_sql = """
           CREATE TABLE forvo (
               id integer PRIMARY KEY,
               expression text,
               speaker text NOT NULL,
               file text NOT NULL
           );
        """
        # adding `speaker` will cause the 2nd query (ORDER BY speaker) to be a no-op
        # I believe theoretically, the 1st query will be faster as well, because
        # no extra binary search is required to get the speaker (a scan can be done instead)
        create_index_sql = f"""
            CREATE INDEX idx_forvo ON nhk16(expression, speaker);
        """

        sql = "INSERT INTO forvo (expression, speaker, file) VALUES (?,?,?)"
        with sqlite3.connect(get_db_path()) as conn:
            cur = conn.cursor()
            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)

            for root, _, files in os.walk(start, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    relative_path = os.path.relpath(path, start)

                    if not name.endswith('.mp3'):
                        print(f"(ForvoAudioSource) skipping non-mp3 file: {relative_path}")
                        continue

                    speaker = os.path.basename(root)
                    expr = os.path.splitext(name)[0]

                    cur.execute(sql, (expr, speaker, relative_path))
            conn.commit()

    def get_name(self, row):
        return f"Forvo ({row[1]})" # user

    def get_sources(
        self, cursor: sqlite3.Connection, qcomp: QueryComponents
    ) -> AudioSourceJsonList:

        audio_source_json_list = []

        if len(qcomp.user) > 0:
            args = [qcomp.expression] + qcomp.user
            # "?,?,?" for number of users
            n_question_marks = ','.join(['?'] * len(qcomp.user))
            rows = cursor.execute(
                f"SELECT file,speaker FROM forvo WHERE expression = ? and speaker IN ({n_question_marks})", (args)).fetchall()

            name_to_audio_source_json: dict[str, AudioSourceJsonEntry] = {}

            for row in rows:
                file_path = row[0]
                found_name = row[1]

                url = self.construct_file_url(file_path)
                name = self.get_name(row)

                audio_source_entry = {"name": name, "url": url}
                name_to_audio_source_json[found_name] = audio_source_entry

            # ensures order in terms of qcomp.user
            for u in qcomp.user:
                audio_source_json_list.append(name_to_audio_source_json[u])

        else:
            rows = cursor.execute(
                "SELECT file,speaker FROM forvo WHERE expression = ? ORDER BY speaker", ([qcomp.expression])).fetchall()
            for row in rows:
                file_path = row[0]
                found_name = row[1]

                url = self.construct_file_url(file_path)
                name = self.get_name(row)

                audio_source_entry = {"name": name, "url": url}
                audio_source_json_list.append(audio_source_entry)

        return audio_source_json_list

FORVO_DATA = AudioSourceData("forvo", "forvo", "user_files/forvo_files")
FORVO_AUDIO_SOURCE = ForvoAudioSource(FORVO_DATA)

