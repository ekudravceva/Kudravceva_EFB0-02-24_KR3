import sqlite3

def create_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Table 'users' created successfully")

if __name__ == "__main__":
    create_table()