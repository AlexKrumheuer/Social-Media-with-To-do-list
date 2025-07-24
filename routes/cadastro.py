from flask import Flask,Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
bp = Blueprint("cadastro", __name__, url_prefix="/")

@bp.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        firstname = request.form.get("first_name")
        lastname = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("senha")

        #Verify
        if not firstname or not lastname or not username or not email or not password:
            message = "Please, fill all the fields"
            return render_template("registrar.html", mensagem=message)
        
        #Gera hash
        password_hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""INSERT INTO usuarios (firstname, lastname, username, email, senha, bio, imagemPerfil) 
                           VALUES (?,?,?,?,?,?,?)""", (firstname, lastname, username, email, password_hashed,"", "uploads/perfil.jpg"))
            conn.commit()
            return redirect(url_for("login.index"))
        except sqlite3.IntegrityError:
            message = "This email was already taken"
        finally:
            conn.close()
    return render_template("registrar.html", mensagem=message)
