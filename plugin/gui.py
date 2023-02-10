from aqt import mw
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom, showInfo
from aqt.operations import QueryOp

from .database import init_db


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
    init_db(True)
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
    pass

def generate_android_database_success():
    showInfo(f"Local audio database for AnkiConnect Android was successfully generated!")


def init_gui():
    # separator
    mw.form.menuTools.addSeparator()

    # re-generate database
    action = QAction("Regenerate Local Audio database", mw)
    qconnect(action.triggered, regenerate_database_operation)
    mw.form.menuTools.addAction(action)

    # re-generate database
    action2 = QAction("Generate Android Database", mw)
    qconnect(action2.triggered, generate_android_database_operation)
    mw.form.menuTools.addAction(action2)

