import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS usuarios;")

conn.commit()
conn.close()

print("Tabela excluída com sucesso!")