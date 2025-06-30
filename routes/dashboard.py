from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import os

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route("/", methods=["GET", "POST"])
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login.index"))
    email_usuario = session["email"]
    if request.method == "POST":
        titulo = request.form.get("title")
        descricao = request.form.get("description")
        data_local = request.form.get("date")
        status = request.form.get("filetasktype")

        file = request.files.get("file")
        if file and file.filename != "":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            arquivo = filepath
        else:
            arquivo = None


        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tarefas (titulo, descricao, arquivo, data_local, status) VALUES (?,?,?,?,?)
                       """, (titulo, descricao, arquivo, data_local, status))
        conn.commit()
        conn.close()

        return render_template("dashboard.html")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas ORDER BY criadO_em DESC")
    tarefas = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html")

    