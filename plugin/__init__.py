from .server import run_server
from .db_utils import attempt_init_db

attempt_init_db()
run_server()
