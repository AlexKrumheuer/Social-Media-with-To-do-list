import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Busca todas as tarefas
cursor.execute("SELECT * FROM tarefas")
tarefas = cursor.fetchall()

# Exibe no terminal
for tarefa in tarefas:
    print(tarefa)

conn.close()
