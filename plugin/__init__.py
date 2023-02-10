from .server import run_server
from .gen_db import attempt_init_db

attempt_init_db()
run_server()
