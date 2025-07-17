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

#Rota para logout
@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login.index"))

#Rota para mensagens
@bp.route("/mensagens", methods=["GET"])
def mensagens():
    return render_template("mensagens.html")

#Rota para amigos
@bp.route("/friends", methods=["GET"])
def friends():
    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Eu enviei
    cursor.execute("""
        SELECT usuarios.id, usuarios.username
        FROM relationship
        JOIN usuarios ON relationship.amigo_id = usuarios.id
        WHERE relationship.usuario_id = ? AND relationship.status = 'friends'
    """, (usuario_id,))

    friend_sent = cursor.fetchall()

    # Eu recebi
    cursor.execute("""
        SELECT usuarios.id, usuarios.username
        FROM relationship
        JOIN usuarios ON relationship.usuario_id = usuarios.id
        WHERE relationship.amigo_id = ? AND relationship.status = 'friends'
    """, (usuario_id,))

    friend_received = cursor.fetchall()
    print(friend_received)
    friendslist = friend_sent + friend_received
    conn.close()
    print(f"Amigos {friendslist}")
    return render_template("allfriends.html", friendslist=friendslist)

#Rota para requests de amizade
@bp.route("/requests", methods=["GET"])
def requests():

    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT relationship.id AS rel_id, usuarios.id AS user_id, usuarios.username
FROM relationship 
JOIN usuarios ON relationship.usuario_id = usuarios.id
WHERE relationship.amigo_id = ? AND relationship.status = 'pendente'
""", (usuario_id,))
    
    usuarios = cursor.fetchall()
    conn.close()

    return render_template("friend-request.html", usuarios=usuarios)

#Rota para sugestões de amizade
@bp.route("/suggestions", methods=["GET"])
def suggestions():

    usuario_id = session.get("usuario_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.username
FROM usuarios u
WHERE u.id != :usuario_id
AND u.id NOT IN (
    SELECT amigo_id FROM relationship
    WHERE usuario_id = :usuario_id
    AND status IN ('friends', 'pendente')
)
AND u.id NOT IN (
    SELECT usuario_id FROM relationship
    WHERE amigo_id = :usuario_id
    AND status IN ('friends', 'pendente')
);
""", (usuario_id,))
    
    usuarios = cursor.fetchall()
    conn.close()

    return render_template("friends-suggestions.html", usuarios=usuarios)

#Rota para enviar sugestão de amizade
@bp.route("/add_friend", methods=["POST"])
def add_friend():
    data = request.get_json()
    usuario_id = session.get("usuario_id")
    amigo_id = data.get("amigo_id")

    if not usuario_id or not amigo_id:
        return jsonify({"success": False, "error": "IDs inválidos"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO relationship (usuario_id, amigo_id, status)
        VALUES (?, ?, ?)
""", (usuario_id, amigo_id, "pendente"))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

#Rota para aceitar pedido de amizade
@bp.route("/accept_request", methods=["POST"])
def accept_request():
    data = request.get_json()
    usuario_id = session.get("usuario_id")
    amigo_id = data.get("amigo_id")

    if not usuario_id or not amigo_id:
        return jsonify({"success": False, "error": "IDs inválidos"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE relationship 
    SET status = ?
    WHERE usuario_id = ? AND amigo_id = ?
""", ('friends', amigo_id, usuario_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


#Rota para acessar dados dos usuarios
@bp.route("/get_user")
def get_user():
    usuario_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, username, email FROM usuarios WHERE id = ? ", (usuario_id,))
    usuario_data = cursor.fetchall()
    usuarios = [{'firstname': row[0], 'lastname': row[1], 'username': row[2], 'email': row[3]} for row in usuario_data]
    conn.close()
    return jsonify(usuarios)

#Rota para alterar configurações de perfil
@bp.route("/config_user", methods=["POST"])
def config_user():
    data = request.get_json()
    usuario_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cursor.fetchone()
    if not usuario:
        return jsonify({"success": False, "error": "Usuario não encontrada ou acesso negado"}), 403
    
    # Extrai os dados antigos
    old_data = dict(usuario)  # converte o Row em dict

    # Usa os dados enviados *se* existirem, senão usa os antigos
    updated_data = {
        "firstname": data.get("firstName") or old_data["firstname"],
        "lastname":  data.get("lastName") or old_data["lastname"],
        "username":  data.get("username") or old_data["username"],
        "email":     data.get("email") or old_data["email"],
    }

    cursor.execute("""
        UPDATE usuarios
        SET firstname = ?, lastname = ?, username = ?, email = ?
        WHERE id = ?
    """, (updated_data['firstname'], updated_data['lastname'], updated_data['username'], updated_data['email'], usuario_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})