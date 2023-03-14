from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from aqt.operations import QueryOp

import time

from .db_utils import (
    init_db,
    android_gen,
    get_num_files_per_source,
    table_exists_and_has_data,
    table_must_be_updated,
)


def attempt_init_db_gui():
    """
    attempts to initialize the db
    if not initialized, runs with gui instead of freezing Anki
    """

    if not table_exists_and_has_data():
        regenerate_database_operation()
    elif table_must_be_updated():
        regenerate_database_operation("Updating local audio database.")


def regenerate_database_operation(msg=False):
    # for some reason, the qconnect call seems to pass in the "false" argument to msg
    if not msg:
        msg = "Generating local audio database."

    start_time = time.time()

    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda _: regenerate_database_action(),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda _: regenerate_database_success(start_time),
    )

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.with_progress(
        f"{msg}\nThis may take a while..."
    ).run_in_background()


def regenerate_database_action() -> int:
    init_db()
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


def action_get_num_files_per_source():
    showInfo(get_num_files_per_source())


def init_gui():
    # must use a hook, so Anki can actually show the process window
    gui_hooks.main_window_did_init.append(attempt_init_db_gui)

    menu_local_audio = mw.form.menuTools.addMenu("Local Audio Server")

    # regenerate regular database (entries.db)
    action = QAction("Regenerate database", mw)
    qconnect(action.triggered, regenerate_database_operation)
    menu_local_audio.addAction(action)

    action2 = QAction("Get number of entries per source", mw)
    qconnect(action2.triggered, action_get_num_files_per_source)
    menu_local_audio.addAction(action2)

    # generate android db (android.db)
    action3 = QAction("Generate Android database", mw)
    qconnect(action3.triggered, generate_android_database_operation)
    menu_local_audio.addAction(action3)
