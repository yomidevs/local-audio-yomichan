import time
import sqlite3
from typing import Optional

from aqt import mw, gui_hooks
from aqt.qt import qconnect, QAction
from aqt.utils import showInfo
from aqt.operations import QueryOp

from .db_utils import (
    init_db,
    android_gen,
    get_num_files_per_source,
    table_exists_and_has_data,
    table_must_be_updated,
    get_count,
    get_unique_count,
)

from .util import get_db_file
from .config import ALL_SOURCES


def attempt_init_db_gui():
    """
    attempts to initialize the db
    if not initialized, runs with gui instead of freezing Anki
    """

    if not table_exists_and_has_data():
        regenerate_database_operation()
    elif table_must_be_updated():
        regenerate_database_operation("Updating local audio database.")


def regenerate_database_operation(msg: Optional[str]=None):
    # for some reason, the qconnect call seems to pass in the "false" argument to msg
    if not msg:
        msg = "Generating local audio database."

    base_msg = f"{msg}\nThis may take a while."

    start_time = time.time()

    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda _: regenerate_database_action(base_msg),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda _: regenerate_database_success(start_time),
    )

    # ASSUMPTION: ALL_SOURCES is insertion ordered
    # ASSUMPTION 2: ALL_SOURCES has at least one source (why would you have zero sources defined?)
    # ASSUMPTION 3: We must actually get the first source here, because the initial callback
    #   runs too early? for the popup to properly update.
    first_source = next(iter(ALL_SOURCES.values()))
    start_msg = base_msg + f"\n\nAdding entries from {first_source.data.id}..."

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.with_progress(start_msg).run_in_background()


def regenerate_database_action(progress_msg: str) -> int:
    def callback(msg: str):
        mw.taskman.run_on_main(
            lambda: mw.progress.update(
                label=progress_msg + "\n\n" + msg,
            )
        )

    init_db(callback)
    return 1


def regenerate_database_success(start_time: float) -> None:
    end_time = time.time()
    total_time = "{:.1f}".format(end_time - start_time)

    showInfo(f"Local audio database was successfully regenerated in {total_time} seconds!")


def generate_android_database_operation():
    start_time = time.time()

    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda _: generate_android_database_action(),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda _: generate_android_database_success(start_time),
    )

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.with_progress(
        "Generating local audio database (for Android).\nThis may take a while..."
    ).run_in_background()


def generate_android_database_action():
    android_gen()
    return 1


def generate_android_database_success(start_time: float):
    end_time = time.time()
    total_time = "{:.1f}".format(end_time - start_time)

    showInfo(
        f"Local audio database for AnkiConnect Android was successfully generated in {total_time} seconds!"
    )


def show_stats():
    with sqlite3.connect(get_db_file()) as conn:
        count = get_count(conn)
        files_per_source = get_num_files_per_source(conn)
        unique_count = get_unique_count(conn)

        if count == 0:
            msg = "Database is empty."
        else:
            files_per_source_str = "<br>".join(f"{f}: {src_count}" for f, src_count in files_per_source.items())

            msg = f"""{files_per_source_str}<br>
            <br>
            Unique: {unique_count}<br>
            Total: {count}
            """
        showInfo(msg, title="Local Audio Statistics")



def init_gui():
    # must use a hook, so Anki can actually show the process window
    gui_hooks.main_window_did_init.append(attempt_init_db_gui)

    menu_local_audio = mw.form.menuTools.addMenu("Local Audio Server")

    # regenerate regular database (entries.db)
    action = QAction("Regenerate database", mw)
    qconnect(action.triggered, regenerate_database_operation)
    menu_local_audio.addAction(action)

    action2 = QAction("Show statistics", mw)
    qconnect(action2.triggered, show_stats)
    menu_local_audio.addAction(action2)

    # generate android db (android.db)
    action3 = QAction("Generate Android database", mw)
    qconnect(action3.triggered, generate_android_database_operation)
    menu_local_audio.addAction(action3)
