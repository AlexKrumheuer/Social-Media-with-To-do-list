from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt

bp = Blueprint("cadastro", __name__, url_prefix="/")

@bp.route("/", methods=["GET", "POST"])
def index():
    mensagem = ""
    if request.method == "POST":
        firstname = request.form.get("first_name")
        lastname = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        senha = request.form.get("senha")

        #validar campos
        if not firstname or not lastname or not username or not email or not senha:
            mensagem = "Por favor, preencha todos os campos"
            return render_template("registrar.html", mensagem=mensagem)
        
        #Gera hash
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO usuarios (firstname, lastname, username, email, senha) VALUES (?,?,?,?,?)", (firstname, lastname, username, email, senha_hash))
            conn.commit()
            mensagem = "Usuário cadastrado com sucesso"
            return redirect(url_for("login.index"))
        except sqlite3.IntegrityError:
            mensagem = "Email já cadastrado"
        finally:
            conn.close()
    return render_template("registrar.html", mensagem=mensagem)
