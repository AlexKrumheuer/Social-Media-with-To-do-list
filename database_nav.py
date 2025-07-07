import sqlite3

db_name = ("database.db")

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    descricao TEXT,
    file TEXT,
    data_local TEXT,
    status TEXT,
    created TEXT,
    usuario_id INTEGER    
               )
""")

conn.commit()
conn.close()

