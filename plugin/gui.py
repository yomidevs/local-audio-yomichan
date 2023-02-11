from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from aqt.operations import QueryOp

from .db_utils import init_db, android_gen


def regenerate_database_operation():
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda _: regenerate_database_action(),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda _: regenerate_database_success(),
    )

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.with_progress().run_in_background()


def regenerate_database_action() -> int:
    init_db()
    return 1


def regenerate_database_success() -> None:
    showInfo(f"Local audio database was successfully regenerated!")


def generate_android_database_operation():
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda _: generate_android_database_action(),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda _: generate_android_database_success(),
    )

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.with_progress().run_in_background()


def generate_android_database_action():
    android_gen()
    return 1


def generate_android_database_success():
    showInfo(
        f"Local audio database for AnkiConnect Android was successfully generated!"
    )


def init_gui():
    mw.form.menuTools.addSeparator()
    menu_local_audio = mw.form.menuTools.addMenu("Local Audio")

    # regenerate regular database (entries.db)
    action = QAction("Regenerate database", mw)
    qconnect(action.triggered, regenerate_database_operation)
    menu_local_audio.addAction(action)

    # generate android db (android.db)
    action2 = QAction("Generate Android database", mw)
    qconnect(action2.triggered, generate_android_database_operation)
    menu_local_audio.addAction(action2)
