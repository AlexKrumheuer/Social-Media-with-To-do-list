import sqlite3

#Cria o banco de dados (ou conecta se já existir)
conexao = sqlite3.connect('database.db')
cursor = conexao.cursor()

#Cria a tabela de usuários
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
)
''')

#Insere usuário de teste com e-mail
cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?,?)", ("admin@admin.com", "1234"))

conexao.commit()
conexao.close()

print("Banco de dados com e-mail criado com sucesso.")