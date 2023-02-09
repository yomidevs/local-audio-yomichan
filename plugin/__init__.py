import http.server
import os
from pathlib import Path
import socketserver
import json
import sqlite3
import threading

from http import HTTPStatus
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs

from .make_nhk16_db import make_nhk16_table

HOSTNAME = "localhost"
PORT = 5050

"""
CONSTANTS

*_SOURCE_PARAM
used for the Custom URL (JSON) setting in Yomichan
e.g. ?sources=jpod,nhk16

*_PATH
used for routing audio GET requests from Yomichan

*_MEDIA_DIR
the media folder within the addon directory

"""

DB_FILE = "entries.db"

JPOD_SOURCE_PARAM = "jpod"
JPOD_PATH = "jpod_audio"
JPOD_MEDIA_DIR = "user_files/jpod_files"

JPOD_ALT_SOURCE_PARAM = "jpod_alternate"
JPOD_ALT_PATH = "jpod_alternate_audio"
JPOD_ALT_MEDIA_DIR = "user_files/jpod_alternate_files"

NHK98_SOURCE_PARAM = "nhk98"
NHK98_PATH = "nhk98_audio"
NHK98_MEDIA_DIR = "user_files/nhk98_files"

NHK16_SOURCE_PARAM = "nhk16"
NHK16_PATH = "nhk16_audio"
NHK16_MEDIA_DIR = "user_files/nhk16_files"

FORVO_SOURCE_PARAM = "forvo"
FORVO_PATH = "forvo_audio"
FORVO_MEDIA_DIR = "user_files/forvo_files"
FORVO_DB_NAME = "forvo.db"


def is_kana(word):
    for char in word:
        if char < 'ぁ' or char > 'ヾ':
            return False
    return True


def get_program_root_path():
    return os.path.dirname(os.path.realpath(__file__)).replace("\\", "/").removesuffix("/")


def table_exists_and_has_data(table_name):
    db_file = get_program_root_path() + "/" + DB_FILE
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = :name",
                       {"name": table_name})
        result = cursor.fetchone()
        if int(result[0]) == 0:
            return False
        cursor.execute(f"SELECT count(*) FROM {table_name}")
        result = cursor.fetchone()
        has_data = int(result[0]) > 0
        cursor.close()
        return has_data


def init_db():
    print("Initializing database. This make take a while...")
    init_jpod_table("jpod", JPOD_MEDIA_DIR)
    init_jpod_table("jpod_alt", JPOD_ALT_MEDIA_DIR)
    init_nhk98_table()
    init_nhk16_table()
    init_forvo_table()
    print("Finished initializing database!")


def init_jpod_table(table_name, media_dir):
    if table_exists_and_has_data(table_name):
        return
    db_file = get_program_root_path() + "/" + DB_FILE
    drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
    create_table_sql = f"""
       CREATE TABLE {table_name} (
           id integer PRIMARY KEY,
           expression text,
           reading text NOT NULL,
           file text NOT NULL
       );
    """
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)
        start = get_program_root_path() + "/" + media_dir
        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                if not name.endswith('.mp3'):
                    continue
                parts = name.removesuffix('.mp3').split(" - ")
                if len(parts) != 2:
                    continue
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)
                sql = f"INSERT INTO {table_name} (expression, reading, file) VALUES (?,?,?)"
                if parts[0] == parts[1]:
                    if is_kana(parts[0]):
                        cur.execute(sql, ('', parts[0], relative_path))
                    else:
                        cur.execute(sql, (parts[0], '', relative_path))
                else:
                    cur.execute(sql, (parts[1], parts[0], relative_path))
        conn.commit()


def init_nhk98_table():
    if table_exists_and_has_data("nhk98"):
        return
    drop_table_sql = "DROP TABLE IF EXISTS nhk98"
    create_table_sql = """
       CREATE TABLE nhk98 (
           id integer PRIMARY KEY,
           expression text,
           reading text NOT NULL,
           file text NOT NULL
       );
    """
    db_file = get_program_root_path() + "/" + DB_FILE
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)
        start = get_program_root_path() + "/" + NHK98_MEDIA_DIR
        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                if not name.endswith('.mp3'):
                    continue
                parts = name.split(".")[0].split("_")
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)
                sql = "INSERT INTO nhk98 (expression, reading, file) VALUES (?,?,?)"
                for part in parts:
                    if is_kana(part):
                        cur.execute(sql, ('', part, relative_path))
                    else:
                        cur.execute(sql, (part, '', relative_path))
        conn.commit()


def init_nhk16_table():
    if not table_exists_and_has_data("nhk16"):
        db_file = get_program_root_path() + "/" + DB_FILE
        make_nhk16_table(NHK16_MEDIA_DIR, db_file)


def init_forvo_table():
    if table_exists_and_has_data("forvo"):
        return
    drop_table_sql = "DROP TABLE IF EXISTS forvo"
    create_table_sql = """
       CREATE TABLE forvo (
           id integer PRIMARY KEY,
           expression text,
           speaker text NOT NULL,
           file text NOT NULL
       );
    """
    sql = "INSERT INTO forvo (expression, speaker, file) VALUES (?,?,?)"
    db_file = get_program_root_path() + "/" + DB_FILE
    with sqlite3.connect(db_file) as conn:
        cur = conn.cursor()
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)
        start = get_program_root_path() + "/" + FORVO_MEDIA_DIR

        for root, _, files in os.walk(start, topdown=False):
            for name in files:
                if not name.endswith('.mp3'):
                    continue

                speaker = os.path.basename(root)
                expr = os.path.splitext(name)[0]
                path = os.path.join(root, name)
                relative_path = os.path.relpath(path, start)

                cur.execute(sql, (expr, speaker, relative_path))
        conn.commit()



class AccentHandler(http.server.SimpleHTTPRequestHandler):
    def log_error(self, *args, **kwargs):
        """By default, SimpleHTTPRequestHandler logs to stderr.  This would
        cause Anki to show an error, even on successful requests
        log_error is still a useful function though, so replace it
        with the inherited log_message."""
        super().log_message(*args, **kwargs)

    def log_message(self, *args):
        """Make log_message do nothing."""
        pass

    def get_jpod_sources(self, cursor, term, reading):
        audio_sources = []
        cursor.execute("SELECT DISTINCT file FROM jpod WHERE expression = :expression AND reading = :reading",
                       {"expression": term, "reading": reading})
        for row in cursor.fetchall():
            audio_sources.append({"name": "JPod101",
                                  "url": f"http://{HOSTNAME}:{PORT}/{JPOD_PATH}/{quote(row[0])}"})
        return audio_sources

    def get_jpod_alt_sources(self, cursor, term, reading):
        audio_sources = []
        cursor.execute("SELECT DISTINCT file FROM jpod_alt WHERE expression = :expression AND reading = :reading",
                       {"expression": term, "reading": reading})
        for row in cursor.fetchall():
            audio_sources.append({"name": "JPod101 Alt",
                                  "url": f"http://{HOSTNAME}:{PORT}/{JPOD_ALT_PATH}/{quote(row[0])}"})
        return audio_sources

    def get_nhk98_sources(self, cursor, term, reading):
        audio_sources = []
        cursor.execute("""
            SELECT file FROM nhk98 WHERE expression = :expression
             UNION
            SELECT file FROM nhk98 WHERE reading = :reading
               AND NOT EXISTS (SELECT file FROM nhk98 WHERE expression = :expression)
        """, {"expression": term, "reading": reading})
        for row in cursor.fetchall():
            audio_sources.append({"name": "NHK98",
                                  "url": f"http://{HOSTNAME}:{PORT}/{NHK98_PATH}/{quote(row[0])}"})
        return audio_sources

    def get_nhk16_sources(self, cursor, term, reading):
        audio_sources = []
        cursor.execute("""
            SELECT display, file FROM nhk16 WHERE expression = :expression AND reading = :reading
             UNION
            SELECT display, file FROM nhk16 WHERE expression = :expression
               AND NOT EXISTS (SELECT display, file FROM nhk16 WHERE expression = :expression AND reading = :reading)
             UNION
            SELECT display, file FROM nhk16 WHERE reading = :reading
               AND NOT EXISTS (SELECT display, file FROM nhk16 WHERE expression = :expression)
        """, {"expression": term, "reading": reading})
        rows = cursor.fetchall()
        for row in rows:
            audio_sources.append({"name": f"NHK16 {row[0]}",
                                  "url": f"http://{HOSTNAME}:{PORT}/{NHK16_PATH}/{quote(row[1])}"})
        return audio_sources

    def get_forvo_sources(self, cursor: sqlite3.Cursor, term: str, users: list[str]):
        audio_sources = []

        if len(users) > 0:
            args = [term] + users
            # "?,?,?" for number of users
            n_question_marks = ','.join(['?'] * len(users))
            rows = cursor.execute(
                f"SELECT speaker,file FROM forvo WHERE expression = ? and speaker IN ({n_question_marks}) ORDER BY speaker", (args)).fetchall()

            for u in users:
                for row in rows:
                    found_name = row[0]
                    if (u == found_name):
                        audio_sources += [
                            {"name": "Forvo: " + found_name, "url": f"http://{HOSTNAME}:{PORT}/{FORVO_PATH}/{row[1]}"}]


        else:
            rows = cursor.execute(
                "SELECT speaker,file FROM forvo WHERE expression = ? ORDER BY speaker", ([term])).fetchall()
            for row in rows:
                found_name = row[0]
                audio_sources += [{"name": "Forvo: " + found_name,
                                   "url": f"http://{HOSTNAME}:{PORT}/{FORVO_PATH}/{row[1]}"}]

        return audio_sources

    def get_audio(self, media_dir, path_prefix):
        audio_file = get_program_root_path() + \
            f"/{media_dir}/" + \
            unquote(self.path).removeprefix(f"/{path_prefix}/")
        if not Path(audio_file).is_file():
            self.send_response(400)
            return
        elif audio_file.endswith(".mp3"):
            self.send_response(200)
            self.send_header('Content-type', 'text/mpeg')
        elif audio_file.endswith(".aac"):
            self.send_response(200)
            self.send_header('Content-type', 'text/aac')
        else:
            self.send_response(400)
            return
        self.end_headers()
        with open(audio_file, 'rb') as fh:
            self.wfile.write(fh.read())

    def parse_query_components(self) -> tuple[str, str, list[str], list[str]]:
        """Extract 'term', 'reading', 'sources', and 'user' query parameters"""
        query_components = parse_qs(urlparse(self.path).query)
        term = query_components["term"][0] if "term" in query_components else ""
        if term == "":
            # Yomichan used to use "expression" but renamed to term.
            # Still support "expression" for older versions
            term = query_components["expression"][0] if "expression" in query_components else ""
        reading = query_components["reading"][0] if "reading" in query_components else ""
        sources = query_components["sources"][0].split(',') if "sources" in query_components else [NHK16_SOURCE_PARAM, NHK98_SOURCE_PARAM, JPOD_SOURCE_PARAM, JPOD_ALT_SOURCE_PARAM, FORVO_SOURCE_PARAM]
        user = [u.strip() for u in query_components["user"][0].split(
            ',')] if "user" in query_components else []

        return term, reading, sources, user

    def do_GET(self):
        if self.path.startswith(f"/{JPOD_PATH}/"):
            self.get_audio(JPOD_MEDIA_DIR, JPOD_PATH)
            return
        elif self.path.startswith(f"/{JPOD_ALT_PATH}/"):
            self.get_audio(JPOD_ALT_MEDIA_DIR, JPOD_ALT_PATH)
            return
        elif self.path.startswith(f"/{NHK98_PATH}/"):
            self.get_audio(NHK98_MEDIA_DIR, NHK98_PATH)
            return
        elif self.path.startswith(f"/{NHK16_PATH}/"):
            self.get_audio(NHK16_MEDIA_DIR, NHK16_PATH)
            return
        elif self.path.startswith(f"/{FORVO_PATH}/"):
            self.get_audio(FORVO_MEDIA_DIR, FORVO_PATH)
            return

        term, reading, sources, users = self.parse_query_components()

        audio_sources = []
        db_file = get_program_root_path() + "/" + DB_FILE
        with sqlite3.connect(db_file) as connection:
            cursor = connection.cursor()
            for source in sources:
                if source == JPOD_SOURCE_PARAM:
                    audio_sources += self.get_jpod_sources(cursor, term, reading)
                elif source == JPOD_ALT_SOURCE_PARAM:
                    audio_sources += self.get_jpod_alt_sources(cursor, term, reading)
                elif source == NHK98_SOURCE_PARAM:
                    audio_sources += self.get_nhk98_sources(cursor, term, reading)
                elif source == NHK16_SOURCE_PARAM:
                    audio_sources += self.get_nhk16_sources(cursor, term, reading)
                elif source == FORVO_SOURCE_PARAM:
                    audio_sources += self.get_forvo_sources(cursor, term, users)
            cursor.close()

        # Build JSON that yomichan requires
        # Ref: https://github.com/FooSoft/yomichan/blob/master/ext/data/schemas/custom-audio-list-schema.json
        resp = {"type": "audioSourceList",
                "audioSources": audio_sources}

        # Writing the JSON contents with UTF-8
        payload = bytes(json.dumps(resp), "utf8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except BrokenPipeError:
            self.log_error("BrokenPipe when sending reply")
        return


if __name__ == "__main__":
    # If we're not in Anki, run the server directly and blocking for easier debugging
    print("Running in debug mode...")
    init_db()
    httpd = socketserver.TCPServer((HOSTNAME, PORT), AccentHandler)
    httpd.serve_forever()
else:
    # Else, run it in a separate thread so it doesn't block
    init_db()
    httpd = http.server.ThreadingHTTPServer((HOSTNAME, PORT), AccentHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
