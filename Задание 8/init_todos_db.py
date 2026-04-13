import sqlite3

def create_todos_table():
    conn = sqlite3.connect("todos.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("Table 'todos' created successfully")

if __name__ == "__main__":
    create_todos_table()