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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS relationship(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    amigo_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pendente',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (amigo_id) REFERENCES usuarios(id)
        );
""")

cursor.execute("""
    DELETE FROM relationship;
""")

conn.commit()
conn.close()

