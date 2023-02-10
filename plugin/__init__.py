from .db_utils import attempt_init_db
from .server import run_server
from .gui import init_gui

attempt_init_db()
run_server()
init_gui()
