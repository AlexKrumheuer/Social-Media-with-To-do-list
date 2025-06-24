from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    mensagem = ''
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return redirect(url_for("sucesso"))
        else:
            mensagem = "Email ou senha incorretos."

    return render_template('login.html', mensagem=mensagem)

@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

if __name__ == '__main__':
    app.run(debug=True)
