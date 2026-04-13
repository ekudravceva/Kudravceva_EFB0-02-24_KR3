from fastapi import FastAPI, HTTPException
from database import get_db_connection, TODOS_DATABASE
from models import User, TodoCreate, TodoUpdate, TodoResponse

app = FastAPI()

@app.post("/register")
def register(user: User):
    conn = get_db_connection("users.db")
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "User registered successfully!"}

#Create 
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_db_connection(TODOS_DATABASE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (todo.title, todo.description)
    )
    
    todo_id = cursor.lastrowid
    conn.commit()
    
    # Получаем созданный todo
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    new_todo = cursor.fetchone()
    conn.close()
    
    return TodoResponse(
        id=new_todo["id"],
        title=new_todo["title"],
        description=new_todo["description"],
        completed=bool(new_todo["completed"])
    )

#Read 
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    conn = get_db_connection(TODOS_DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    todo = cursor.fetchone()
    conn.close()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return TodoResponse(
        id=todo["id"],
        title=todo["title"],
        description=todo["description"],
        completed=bool(todo["completed"])
    )

#Update
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_db_connection(TODOS_DATABASE)
    cursor = conn.cursor()
    
    # Проверяем, существует ли todo
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    existing = cursor.fetchone()
    
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Обновляем
    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, todo.completed, todo_id)
    )
    
    conn.commit()
    
    # Получаем обновленный todo
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    updated_todo = cursor.fetchone()
    conn.close()
    
    return TodoResponse(
        id=updated_todo["id"],
        title=updated_todo["title"],
        description=updated_todo["description"],
        completed=bool(updated_todo["completed"])
    )

# Delete 
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection(TODOS_DATABASE)
    cursor = conn.cursor()
    
    # Проверяем, существует ли todo
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    existing = cursor.fetchone()
    
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Удаляем
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Todo deleted successfully"}