import os
from pathlib import Path
import sqlite3

from typing import Any

from .util import get_android_db_path, get_db_path, get_program_root_path, QueryComponents
from .all_sources import SOURCES

def android_gen():
    original_db_path = get_db_path()
    android_db_path = get_android_db_path()
    with sqlite3.connect(original_db_path) as connection:
        og_cursor = connection.cursor()
        with sqlite3.connect(android_db_path) as android_connection:
            android_cursor = android_connection.cursor()

            android_write(og_cursor, android_cursor)

            android_cursor.close()
        og_cursor.close()

# original cursor, android cursor
def android_write(og_cur, a_cur):

    drop_table_sql = f"DROP TABLE IF EXISTS android"
    create_table_sql = f"""
       CREATE TABLE android (
           file text NOT NULL,
           source text NOT NULL,
           data blob NOT NULL
       );
    """
    create_index_sql = f"""
        CREATE INDEX idx_android ON android(file, source);
    """
    a_cur.execute(drop_table_sql)
    a_cur.execute(create_table_sql)
    a_cur.execute(create_index_sql)

    sql = f"""
        INSERT INTO android (file, source, data) VALUES (?,?,?)
        """

    for source in SOURCES:
        print(f"(android_write) Reading from {source}...")
        all_files_query = f"""
            SELECT file FROM {source.data.id}
            """

        rows = og_cur.execute(all_files_query).fetchall()
        for row in rows:
            file_name = row[0]
            full_file_path = os.path.join(
                get_program_root_path(),
                source.get_media_dir_path(),
                file_name
            )
            if not Path(full_file_path).is_file():
                print(f"(android_write) Cannot find file: {full_file_path}")
                continue

            with open(full_file_path, 'rb') as file:
                a_cur.execute(sql, (file_name, source.data.id, file.read()))



def table_exists_and_has_data() -> bool:
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = :name",
            {"name": "entries"},
        )
        result = cursor.fetchone()
        if int(result[0]) == 0:
            return False
        cursor.execute("SELECT count(*) FROM entries")
        result = cursor.fetchone()
        has_data = int(result[0]) > 0
        cursor.close()
        return has_data

    return False

def attempt_init_db():
    if not table_exists_and_has_data():
        init_db()

def init_db():
    print("Initializing database. This make take a while...")

    original_db_path = get_db_path()
    with sqlite3.connect(original_db_path) as connection:
        cursor = connection.cursor()

        # initializes entries table
        drop_table_sql = "DROP TABLE IF EXISTS entries"
        cursor.execute(drop_table_sql)

        # - expression (term): the main lookup key, potentially in kanji
        # - reading: kana only version of expression. If null, then no reading was
        #   available from the source.
        # - file: file path to the audio
        #   Allows for easier sorting for more ideal results without post processing
        #   or unions + subqueries.
        # - speaker: contains the forvo username. Null for anything that isn't forvo.
        # - display: contains the display for nhk16. Null for anything that isn't nhk16.
        create_table_sql = """
            CREATE TABLE entries (
                id integer PRIMARY KEY,
                expression text NOT NULL,
                reading text,
                source text NOT NULL,
                speaker text,
                display text,
                file text NOT NULL
           );
        """
        cursor.execute(create_table_sql)

        # see AudioSource.execute_query for possible queries

        # I'm assuming the query won't be expanded out into 4 long queries,
        # so these indices are necessary for each side of the OR statements.
        create_idx_reading_sql = f"""
            CREATE INDEX idx_reading ON entries(reading);
        """
        cursor.execute(create_idx_reading_sql)
        create_idx_speaker_sql = f"""
            CREATE INDEX idx_speaker ON entries(speaker);
        """
        cursor.execute(create_idx_speaker_sql)

        # optimize first query
        create_idx_expr_reading_sql = f"""
            CREATE INDEX idx_expr_reading ON entries(expression, reading);
        """
        cursor.execute(create_idx_expr_reading_sql)

        # optimize second query
        create_idx_expr_reading_speaker_sql = f"""
            CREATE INDEX idx_reading_speaker ON entries(expression, reading, speaker);
        """
        cursor.execute(create_idx_expr_reading_speaker_sql)

        # optimize third query
        create_idx_expr_reading_speaker_sql = f"""
            CREATE INDEX idx_all ON entries(expression, reading, source);
        """
        cursor.execute(create_idx_expr_reading_speaker_sql)
        cursor.close()


        for source in SOURCES:
            print(f"(init_db) Adding entries from {source.data.id}...")
            source.add_entries(connection)

    print("Finished initializing database!")


#def execute_query(
#    self, cursor: sqlite3.Connection, **params: dict[str, str]
#) -> list[Any]:
def execute_query(
    cursor: sqlite3.Connection, qcomps: QueryComponents
) -> list[Any]:

    # - short hand is (expression = :expression AND (reading = :reading OR reading IS NULL))
    #   - expanded out statement such that the query explicit, which ensures the index is properly used
    # - order by priority is to prevent:
    #   - unnecessary post processing (best done in the query)
    #   - unnecessary unions & subqueries
    #   - NOTE: this is now replaced by ordering by reading (currently, priority is
    #     1 if reading is null, and 2 otherwise. Ordering by reading is good enough for now.)
    # - cannot do "expression = :expression or reading = :reading":
    #   - imagine if there existed a word in pure kana that you wanted to add, but there was
    #     a different word that had the same kana
    #   - how to prioritize without subqueries or post processing!
    #   - best for correctness anyways: it is true that we can select any word that
    #     has the same reading, but there's 0 guarantee that the pitch accent will be the same!

    ## the query for when we don't care about speakers
    #query = f"""
    #    SELECT * FROM entries WHERE (
    #            expression = ?
    #        AND (reading IS NULL OR reading = ?)
    #    )
    #    ORDER BY
    #      (CASE source
    #        WHEN ? THEN 0
    #        WHEN ? THEN 1
    #        WHEN ? THEN 2
    #        WHEN ? THEN 3
    #      END),
    #      speaker,
    #      reading
    #    """

    ## the query for when speakers must be filtered
    #query = f"""
    #    SELECT * FROM entries WHERE (
    #             expression = ?
    #        AND (reading IS NULL OR reading = ?)
    #        AND (speaker IN (?,?,?) OR speaker IS NULL)
    #    )
    #    ORDER BY
    #      (CASE source
    #        WHEN ? THEN 0
    #        WHEN ? THEN 1
    #        WHEN ? THEN 2
    #        WHEN ? THEN 3
    #      END),
    #      reading
    #    """

    ## the query for when we have less than all sources
    ## i.e. fovo, jpod, jpod_alternate
    #query = f"""
    #    SELECT * FROM entries WHERE (
    #        AND expression = :expression
    #        AND (reading IS NULL OR reading = :reading)
    #        AND source in (?,?,?)
    #    )
    #    ORDER BY
    #      (CASE source
    #        WHEN ? THEN 0
    #        WHEN ? THEN 1
    #        WHEN ? THEN 2
    #      END),
    #      reading
    #    """

    params = [qcomps.expression, qcomps.reading]

    query_where = f"""
        expression = ?
        AND (reading IS NULL OR reading = ?)
    """

    # filters by sources if necessary
    if len(qcomps.sources) != len(SOURCES):
        n_question_marks = ",".join(["?"] * len(qcomps.sources))
        query_where += f"""
            AND (source in ({n_question_marks}))
        """
        params += qcomps.sources

    # filters by speakers if necessary
    if len(qcomps.user) > 0:
        n_question_marks = ",".join(["?"] * len(qcomps.user))
        query_where += f"""
            AND (speaker in ({n_question_marks}))
        """
        params += qcomps.user

    query_order_source = "\n".join(
        f"WHEN ? THEN {i}" for i in range(len(qcomps.sources))
    )
    params += qcomps.sources

    query = f"""
        SELECT * FROM entries WHERE (
            {query_where}
        )
        ORDER BY
          (CASE source {query_order_source} END),
          reading
        """

    print(query)
    print(params)

    return cursor.execute(query, params).fetchall()

