from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt

bp = Blueprint('login', __name__, url_prefix='/login')#Separa a rota /login

@bp.route('/', methods=['GET', 'POST'])
def index():
    mensagem = ""
    if request.method == 'POST': #Pega dados do usuário
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('database.db')#Coneta com o DB e verifica se há um email correspondente nesse DB
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario[5]):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[3]
            session["email"] = usuario[4]
            return redirect(url_for('dashboard.index'))
        else:
            mensagem = "Email ou senha incorretos."

    return render_template('login.html', mensagem=mensagem)
