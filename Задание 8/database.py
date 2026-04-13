import sqlite3

USERS_DATABASE = "users.db"
TODOS_DATABASE = "todos.db"

def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn