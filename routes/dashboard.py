from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import json
from datetime import datetime

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#Função auxiliar para conectar no banco
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # Permite acessar por nome (row['titulo'])
    return conn

#Função para buscar e organizar tarefas
def add_tarefas_html():
    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM tarefas WHERE usuario_id=?", (usuario_id,))
    tarefas_db = cursor.fetchall()

    tarefas_dict = []
    for t in tarefas_db:
        tarefa = {
            "id": t["id"],
            "titulo": t["titulo"],
            "descricao": t["descricao"],
            "data_local": t["data_local"],
            "status": t["status"],
        }
        tarefas_dict.append(tarefa)

    # Separar por status
    start = [t for t in tarefas_dict if t["status"] == "start"]
    on_going = [t for t in tarefas_dict if t["status"] == "onGoing"]
    finish = [t for t in tarefas_dict if t["status"] == "finish"]

    tarefas = {
        "start": start,
        "on_going": on_going,
        "finish": finish,
    }

    conn.close()
    return [tarefas, tarefas_dict]

#Rota principal (dashboard)
@bp.route("/", methods=["GET"])
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login.index"))

    lista = add_tarefas_html()
    return render_template("dashboard.html", tarefas=lista[0], tarefasEdit=json.dumps(lista[1]))

#Rota para editar tarefa
@bp.route("/editar_tarefa", methods=["POST"])
def editar_tarefa():
    data = request.get_json()
    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tarefas WHERE id=? AND usuario_id=?", (data["id"], usuario_id))
    tarefa = cursor.fetchone()
    if not tarefa:
        return jsonify({"success": False, "error": "Tarefa não encontrada ou acesso negado"}), 403

    cursor.execute("""
        UPDATE tarefas
        SET titulo = ?, descricao = ?, data_local = ?, status = ?
        WHERE id = ? AND usuario_id = ?
    """, (data['titulo'], data['descricao'], data['data_local'], data['status'], data["id"], usuario_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

#Rota para criar tarefa
@bp.route("/criar_tarefa", methods=["POST"])
def criar_tarefa():
    data = request.get_json()

    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefas (titulo, descricao, data_local, status, usuario_id)
        VALUES (?, ?, ?, ?, ?)
    """, (data['titulo'], data['descricao'], data['data_local'], data['status'], usuario_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

#Rota para remover tarefa
@bp.route("/remover_tarefa", methods=["POST"])
def remover_tarefa():
    data = request.get_json()
    id = data["id"]
    usuario_id = session.get("usuario_id")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tarefas WHERE id=? AND usuario_id=?", (id, usuario_id))
    tarefa = cursor.fetchone()
    if not tarefa:
        return jsonify({"success": False, "error": "Tarefa não encontrada ou acesso negado"}), 403

    cursor.execute("DELETE FROM tarefas WHERE id = ? AND usuario_id=?", (id,usuario_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})
