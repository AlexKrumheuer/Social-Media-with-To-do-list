############################################################# Imports ############################################################
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

############################################################ Initial Configs ############################################################
bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

############################################################ Auxiliar Functions ############################################################
#Function to connect to Database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

#Função para buscar e organizar tarefas
def add_tarefas_html():
    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM tarefas WHERE usuario_id=?", (usuario_id,))
    tarefas_db = cursor.fetchall()
    tarefas_db 

    tarefas_dict = []
    for t in tarefas_db:

        data_formatada = ""
        if t["data_local"]:
            try:
                # Tenta converter com hora (datetime-local)
                dt = datetime.strptime(t["data_local"], "%Y-%m-%dT%H:%M")
                data_formatada = dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                try:
                    # Tenta converter só a data
                    dt = datetime.strptime(t["data_local"], "%Y-%m-%d")
                    data_formatada = dt.strftime("%d/%m/%Y")
                except ValueError:
                    # Mantém como está se não conseguir converter
                    data_formatada = t["data_local"]

        tarefa = {
            "id": t["id"],
            "titulo": t["titulo"],
            "descricao": t["descricao"],
            "data_local": data_formatada,
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (session.get("usuario_id"),))
    usuario = cursor.fetchone()
    lista = add_tarefas_html()
    return render_template("dashboard.html", tarefas=lista[0], tarefasEdit=json.dumps(lista[1]), usuario=usuario)

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
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()

    #SELECT FRIENDS
    cursor.execute("""
SELECT *
FROM usuarios u
JOIN relationship r ON (u.id = r.amigo_id OR u.id = r.usuario_id)
WHERE
    (r.usuario_id = :usuario_id OR r.amigo_id = :usuario_id)
    AND r.status = 'friends'
    AND u.id != :usuario_id
""", (usuario_id,))
    friends = cursor.fetchall()
    conn.close()
    return render_template("mensagens.html", friends=friends)

#Rota to send Messages
@bp.route("/send_message", methods=["POST"])
def send_message():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?,?,?)", (usuario_id, data['destinatario_id'], data['content']))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Messagee was sent successfully"})

@bp.route("/api/messages/<friend_id>")
def api_messages(friend_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender_id, receiver_id, content, strftime('%H:%M', timestamp) AS hora
        FROM messages
        WHERE
            (sender_id = ? AND receiver_id = ?)
            OR  
            (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (usuario_id, friend_id, friend_id, usuario_id))

    messages = cursor.fetchall()
    conn.close()

    messages_list = [dict(m) for m in messages]

    return jsonify(messages_list)


@bp.route("/mensagens_talk/<friend_id>")
def mensagens_talk(friend_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()
    #SELECT FRIENDS TO TALK
    cursor.execute("""
    SELECT * FROM usuarios WHERE id=?
""", (friend_id,))
    friend=cursor.fetchone()
    cursor.execute("""
SELECT *
FROM usuarios u
JOIN relationship r ON (u.id = r.amigo_id OR u.id = r.usuario_id)
WHERE
    (r.usuario_id = :usuario_id OR r.amigo_id = :usuario_id)
    AND r.status = 'friends'
    AND u.id != :usuario_id
""", (usuario_id,))
    friends = cursor.fetchall()

    #SELECT MESSAGES
    cursor.execute("""
    SELECT sender_id, receiver_id, content, strftime('%H:%M', timestamp) AS hora FROM messages
    WHERE
        (sender_id = ? AND receiver_id = ?)
    OR  
        (sender_id = ? AND receiver_id = ?)
    ORDER BY timestamp ASC
""", (usuario_id, friend_id, friend_id, usuario_id))
    messages = cursor.fetchall()
    conn.close()

    return render_template("mensagens-selected.html", friends=friends, friend=friend, messages=messages)



#Rota para amigos
@bp.route("/friends", methods=["GET"])
def friends():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()

    # Eu enviei
    cursor.execute("""
        SELECT usuarios.id, usuarios.username, usuarios.imagemPerfil
        FROM relationship
        JOIN usuarios ON relationship.amigo_id = usuarios.id
        WHERE relationship.usuario_id = ? AND relationship.status = 'friends'
    """, (usuario_id,))

    friend_sent = cursor.fetchall()

    # Eu recebi
    cursor.execute("""
        SELECT usuarios.id, usuarios.username, usuarios.imagemPerfil
        FROM relationship
        JOIN usuarios ON relationship.usuario_id = usuarios.id
        WHERE relationship.amigo_id = ? AND relationship.status = 'friends'
    """, (usuario_id,))

    friend_received = cursor.fetchall()
    friendslist = friend_sent + friend_received
    conn.close()
    return render_template("allfriends.html", friendslist=friendslist)

#Rota para requests de amizade
@bp.route("/requests", methods=["GET"])
def requests():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT relationship.id AS rel_id, usuarios.id AS user_id, usuarios.username, usuarios.imagemPerfil
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
    if not usuario_id:
        return redirect(url_for("login.index"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.username, u.imagemPerfil
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

#Rota para recusar request
@bp.route("/refuse_request/<friend_id>", methods=["GET"])
def refuse_request(friend_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    print(f"Teste agora {friend_id} {usuario_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relationship WHERE usuario_id=? AND amigo_id=?",(friend_id, usuario_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.requests"))

#Rota to unfollow
@bp.route("/unfollow/<friend_id>", methods=["GET"])
def unfollow(friend_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    print(friend_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relationship WHERE (usuario_id=? AND amigo_id=?) OR (usuario_id=? AND amigo_id=?)",(usuario_id, friend_id, friend_id, usuario_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.friends"))


#Rota para acessar dados dos usuarios
@bp.route("/get_user")
def get_user():
    usuario_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, username, email, bio FROM usuarios WHERE id = ? ", (usuario_id,))
    usuario_data = cursor.fetchall()
    usuarios = [{'firstname': row[0], 'lastname': row[1], 'username': row[2], 'email': row[3], 'bio': row[4]} for row in usuario_data]
    conn.close()
    return jsonify(usuarios)

#Rota para alterar configurações de perfil
@bp.route("/config_user", methods=["POST"])
def config_user():
    usuario_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cursor.fetchone()
    if not usuario:
        return jsonify({"success": False, "error": "Usuario não encontrada ou acesso negado"}), 403
    
    # Extrai os dados antigos
    old_data = dict(usuario)  # converte o Row em dict

    form = request.form

    # Usa os dados enviados *se* existirem, senão usa os antigos
    updated_data = {
        "firstname": form.get("firstName") or old_data["firstname"],
        "lastname":  form.get("lastName") or old_data["lastname"],
        "username":  form.get("username") or old_data["username"],
        "email":     form.get("email") or old_data["email"],
        "bio":       form.get("bio") or old_data["bio"],
    }

    session['usuario_nome'] = updated_data['username']
    session["email"] = updated_data['email']

    cursor.execute("""
        UPDATE usuarios
        SET firstname = ?, lastname = ?, username = ?, email = ?, bio = ?
        WHERE id = ?
    """, (updated_data['firstname'], updated_data['lastname'], updated_data['username'], updated_data['email'], updated_data['bio'], usuario_id))
    
    file = request.files.get("profileImage")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join("static/uploads", filename))
        cursor.execute("UPDATE usuarios SET imagemPerfil=? WHERE id=?", (f"uploads/{filename}", usuario_id))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@bp.route("/user/<username>")
def perfil_usuario(username):
    usuario_logado = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,) )
    usuario = cursor.fetchone()
    
    cursor.execute("""
    SELECT 1 FROM relationship
    WHERE ((usuario_id = ? AND amigo_id = ?) OR (usuario_id = ? AND amigo_id = ?))
    AND status == 'friends'
""", (usuario_logado, usuario['id'], usuario['id'], usuario_logado))

    resultado = cursor.fetchone()
    if resultado:
        friends = True
    else:
        friends = False
    conn.close()
    if not usuario:
        return "Usuário não encontrado",  404

    return render_template("perfil-homepage.html", usuario=usuario, usuarioLogado=usuario_logado, status=friends)

@bp.route("/change_password")
def change_password():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))
    return render_template("changePassword.html")

#Rota
@bp.route("/reset_password", methods=["POST"])
def reset_password():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("login.index"))

    form = request.form
    updated_data = {
        "currentPassword": form.get("currentPassword"),
        "newPassword":  form.get("newPassword"),
        "confirmNewPassword":  form.get("confirmNewPassword"),
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    user = cursor.fetchone()

    if not bcrypt.checkpw(updated_data["currentPassword"].encode('utf-8'), user[5]) or updated_data["newPassword"]!=updated_data["confirmNewPassword"]:
        mensagem= "Please verify that your current password is correct and that the new password matches the confirmation"
        conn.close()
        return render_template("changePassword.html", mensagem=mensagem)

    nova_senha_hash = bcrypt.hashpw(updated_data["newPassword"].encode("utf-8"), bcrypt.gensalt())
    cursor.execute("UPDATE usuarios SET senha=? WHERE id=?", (nova_senha_hash, usuario_id))
    conn.commit()
    conn.close()
    session.clear()

    return jsonify({"success": True})

    

