############################################################# Imports ############################################################
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import bcrypt
from functools import wraps

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

#Function to get user's tasks
def get_tasks_by_user():
    usuario_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM tarefas WHERE usuario_id=?", (usuario_id,))
    tasks_db = cursor.fetchall()

    tasks_dict = []
    for t in tasks_db:
        formated_date = ""
        if t["data_local"]:
            try:
                # Try to convert in datetime-local format
                dt = datetime.strptime(t["data_local"], "%Y-%m-%dT%H:%M")
                formated_date = dt.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                try:
                    # Try to convert in date format
                    dt = datetime.strptime(t["data_local"], "%Y-%m-%d")
                    formated_date = dt.strftime("%d/%m/%Y")
                except ValueError:
                    # Maintain state if cannot convert
                    formated_date = t["data_local"]

        task = {
            "id": t["id"],
            "titulo": t["titulo"],
            "descricao": t["descricao"],
            "data_local": formated_date,
            "status": t["status"],
        }
        tasks_dict.append(task)

    # Separate by status
    start = [t for t in tasks_dict if t["status"] == "start"]
    on_going = [t for t in tasks_dict if t["status"] == "onGoing"]
    finish = [t for t in tasks_dict if t["status"] == "finish"]

    tasks_status = {
        "start": start,
        "on_going": on_going,
        "finish": finish,
    }

    conn.close()
    return [tasks_status, tasks_dict]

#Login required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login.index"))
        return f(*args, **kwargs)
    return decorated_function
############################################################ Dashboard Route ############################################################
@bp.route("/", methods=["GET"])
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (session.get("usuario_id"),))
    user = cursor.fetchone()
    taskList = get_tasks_by_user()
    return render_template("dashboard.html", tarefas=taskList[0], tarefasEdit=json.dumps(taskList[1]), usuario=user)



############################################################ Task Session ############################################################


############################################################ Edit Task Route ############################################################
@bp.route("/edit_task", methods=["POST"])
def edit_task():
    data = request.get_json()
    user_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    #Verify if there are any of this user
    cursor.execute("SELECT * FROM tarefas WHERE id=? AND usuario_id=?", (data["id"], user_id))
    task = cursor.fetchone()
    if not task:
        return jsonify({"success": False, "error": "Tarefa não encontrada ou acesso negado"}), 403

    #Update Task
    cursor.execute("""
        UPDATE tarefas
        SET titulo = ?, descricao = ?, data_local = ?, status = ?
        WHERE id = ? AND usuario_id = ?
    """, (data['titulo'], data['descricao'], data['data_local'], data['status'], data["id"], user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

############################################################ Create Task Route ############################################################
@bp.route("/create_task", methods=["POST"])
def create_task():
    data = request.get_json()
    user_id = session.get("usuario_id")

    conn = get_db_connection()
    cursor = conn.cursor()
    #Insert Task into table Tasks
    cursor.execute("""
        INSERT INTO tarefas (titulo, descricao, data_local, status, usuario_id)
        VALUES (?, ?, ?, ?, ?)
    """, (data['titulo'], data['descricao'], data['data_local'], data['status'], user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

############################################################ Remove Task Route ############################################################
@bp.route("/remove_task", methods=["POST"])
def remove_task():
    data = request.get_json()
    id = data["id"]
    user_id = session.get("usuario_id")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    #Select task to be removed
    cursor.execute("SELECT * FROM tarefas WHERE id=? AND usuario_id=?", (id, user_id))
    task = cursor.fetchone()
    #If task is not found, returns an error
    if not task:
        return jsonify({"success": False, "error": "Tarefa não encontrada ou acesso negado"}), 403
    #Remove Task
    cursor.execute("DELETE FROM tarefas WHERE id = ? AND usuario_id=?", (id,user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})






############################################################ Logout Route ############################################################
@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login.index"))



############################################################ Message Routes ############################################################

############################################################ Message Main Route ############################################################
@bp.route("/messages", methods=["GET"])
@login_required
def messages():
    usuario_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    #Select Friends to show in sidebar of message page
    cursor.execute("""
    SELECT * FROM usuarios u
    JOIN relationship r ON (u.id = r.amigo_id OR u.id = r.usuario_id)
    WHERE
        (r.usuario_id = :usuario_id OR r.amigo_id = :usuario_id)
        AND r.status = 'friends'
        AND u.id != :usuario_id """, (usuario_id,))
    friends = cursor.fetchall()
    conn.close()
    return render_template("message.html", friends=friends)

############################################################ Send Message Route ############################################################
@bp.route("/send_message", methods=["POST"])
@login_required
def send_message():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    #Insert message into message Table
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?,?,?)", (user_id, data['receiver_id'], data['content']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Messagee was sent successfully"})

############################################################ Api to load messages on live ############################################################
@bp.route("/api/messages/<friend_id>")
@login_required
def api_messages(friend_id):
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    #Select Messages
    cursor.execute("""
        SELECT sender_id, receiver_id, content, strftime('%H:%M', timestamp) AS hora
        FROM messages
        WHERE
            (sender_id = ? AND receiver_id = ?)
            OR  
            (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (user_id, friend_id, friend_id, user_id))
    messages = cursor.fetchall()
    conn.close()
    #Return message formated
    messages_list = [dict(m) for m in messages]

    return jsonify(messages_list)

############################################################ Route to load conversation page ############################################################
@bp.route("/messages_talk/<friend_id>")
@login_required
def messages_talk(friend_id):
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    #Selects friends to show in sidebar
    cursor.execute("""
    SELECT * FROM usuarios WHERE id=?
""", (friend_id,))
    friend=cursor.fetchone()
    cursor.execute("""
    SELECT * FROM usuarios u
    JOIN relationship r ON (u.id = r.amigo_id OR u.id = r.usuario_id)
    WHERE
        (r.usuario_id = :usuario_id OR r.amigo_id = :usuario_id)
        AND r.status = 'friends'
        AND u.id != :usuario_id """, (user_id,))
    friends = cursor.fetchall()

    #Select messages for the conversation page
    cursor.execute("""
    SELECT sender_id, receiver_id, content, strftime('%H:%M', timestamp) AS hora FROM messages
    WHERE
        (sender_id = ? AND receiver_id = ?)
    OR  
        (sender_id = ? AND receiver_id = ?)
    ORDER BY timestamp ASC """, (user_id, friend_id, friend_id, user_id))
    messages = cursor.fetchall()
    conn.close()

    return render_template("mensagens-selected.html", friends=friends, friend=friend, messages=messages)





############################################################ Friends Routes ############################################################
############################################################ Route to all your friends page ############################################################
@bp.route("/friends", methods=["GET"])
@login_required
def friends():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load Friends that the user sent the friend request
    cursor.execute("""
        SELECT usuarios.id, usuarios.username, usuarios.imagemPerfil
        FROM relationship
        JOIN usuarios ON relationship.amigo_id = usuarios.id
        WHERE relationship.usuario_id = ? AND relationship.status = 'friends'
    """, (user_id,))
    friend_sent = cursor.fetchall()

    # Load Friends that the user received the friend request
    cursor.execute("""
        SELECT usuarios.id, usuarios.username, usuarios.imagemPerfil
        FROM relationship
        JOIN usuarios ON relationship.usuario_id = usuarios.id
        WHERE relationship.amigo_id = ? AND relationship.status = 'friends'
    """, (user_id,))
    friend_received = cursor.fetchall()

    friendslist = friend_sent + friend_received
    conn.close()
    return render_template("allfriends.html", friendslist=friendslist)

############################################################ Route to all your request of friendship page ############################################################
@bp.route("/requests", methods=["GET"])
@login_required
def requests():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    #Select all your requests
    cursor.execute("""
    SELECT relationship.id AS rel_id, usuarios.id AS user_id, usuarios.username, usuarios.imagemPerfil
    FROM relationship 
    JOIN usuarios ON relationship.usuario_id = usuarios.id
    WHERE relationship.amigo_id = ? AND relationship.status = 'pendente' """, (user_id,))
    
    users = cursor.fetchall()
    conn.close()

    return render_template("friend-request.html", usuarios=users)

############################################################ Route to all your suggestions of friendship page ############################################################
@bp.route("/suggestions", methods=["GET"])
@login_required
def suggestions():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    #Select your suggestions in table relationship and usuarios
    cursor.execute("""
    SELECT u.id, u.username, u.imagemPerfil
    FROM usuarios u
    WHERE u.id != :usuario_id
    AND u.id NOT IN (
        SELECT amigo_id FROM relationship
        WHERE usuario_id = :usuario_id
        AND status IN ('friends', 'pendente'))
    AND u.id NOT IN (
        SELECT usuario_id FROM relationship
        WHERE amigo_id = :usuario_id
        AND status IN ('friends', 'pendente')); """, (user_id,))
    
    users = cursor.fetchall()
    conn.close()

    return render_template("friends-suggestions.html", usuarios=users)

############################################################ Route send request of friendship ############################################################
@bp.route("/add_friend", methods=["POST"])
def add_friend():
    data = request.get_json()

    user_id = session.get("usuario_id")
    friend_id = data.get("amigo_id")

    #Verify if those ids exist are not an invalid value
    if not user_id or not friend_id:
        return jsonify({"success": False, "error": "IDs inválidos"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    #Insert the request of friendship into relationship Table
    cursor.execute("""
        INSERT INTO relationship (usuario_id, amigo_id, status)
        VALUES (?, ?, ?) """, (user_id, friend_id, "pendente"))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

############################################################ Route accept request of friendship ############################################################
@bp.route("/accept_request", methods=["POST"])
def accept_request():
    data = request.get_json()
    user_id = session.get("usuario_id")
    friend_id = data.get("amigo_id")

    if not user_id or not friend_id:
        return jsonify({"success": False, "error": "IDs inválidos"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE relationship 
    SET status = ?
    WHERE usuario_id = ? AND amigo_id = ? """, ('friends', friend_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

############################################################ Route refuse request of friendship ############################################################
@bp.route("/refuse_request/<friend_id>", methods=["GET"])
@login_required
def refuse_request(friend_id):
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relationship WHERE usuario_id=? AND amigo_id=?",(friend_id, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.requests"))

############################################################ Route unfollow an user ############################################################
@bp.route("/unfollow/<friend_id>", methods=["GET"])
@login_required
def unfollow(friend_id):
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM relationship WHERE (usuario_id=? AND amigo_id=?) OR (usuario_id=? AND amigo_id=?)",(user_id, friend_id, friend_id, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.friends"))




############################################################ Route config user perfil ############################################################
############################################################ Route to get user info  ############################################################
@bp.route("/get_user")
def get_user():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, username, email, bio FROM usuarios WHERE id = ? ", (user_id,))
    user_data = cursor.fetchall()
    users = [{'firstname': row[0], 'lastname': row[1], 'username': row[2], 'email': row[3], 'bio': row[4]} for row in user_data]
    conn.close()
    return jsonify(users)

############################################################ Route to config user info  ############################################################
@bp.route("/config_user", methods=["POST"])
def config_user():
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    user = cursor.fetchone()
    #Verify if user was found
    if not user:
        return jsonify({"success": False, "error": "Usuario não encontrada ou acesso negado"}), 403
    
    #Get old data user
    old_data = dict(user)  # CConvert into a dict

    form = request.form

    # Update to new data, if there's no new data, maintain old ones
    updated_data = {
        "firstname": form.get("firstName") or old_data["firstname"],
        "lastname":  form.get("lastName") or old_data["lastname"],
        "username":  form.get("username") or old_data["username"],
        "email":     form.get("email") or old_data["email"],
        "bio":       form.get("bio") or old_data["bio"],
    }

    #Update session data
    session['usuario_nome'] = updated_data['username']
    session["email"] = updated_data['email']

    #Update in table user info
    cursor.execute("""
        UPDATE usuarios
        SET firstname = ?, lastname = ?, username = ?, email = ?, bio = ?
        WHERE id = ? """, (updated_data['firstname'], updated_data['lastname'], updated_data['username'], updated_data['email'], updated_data['bio'], user_id))
    
    #Get image file path
    file = request.files.get("profileImage")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join("static/uploads", filename))
        cursor.execute("UPDATE usuarios SET imagemPerfil=? WHERE id=?", (f"uploads/{filename}", user_id))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True})

############################################################ Change password page ############################################################
@bp.route("/change_password")
@login_required
def change_password():
    return render_template("changePassword.html")

############################################################# Reset password route ############################################################
@bp.route("/reset_password", methods=["POST"])
@login_required
def reset_password():
    user_id = session.get("usuario_id")

    form = request.form
    #Get new and old password typed by user
    updated_data = {
        "currentPassword": form.get("currentPassword"),
        "newPassword":  form.get("newPassword"),
        "confirmNewPassword":  form.get("confirmNewPassword"),
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    user = cursor.fetchone()

    #Verify if the old password matchs and if the newPassword and its confirmation match
    if not bcrypt.checkpw(updated_data["currentPassword"].encode('utf-8'), user[5]) or updated_data["newPassword"]!=updated_data["confirmNewPassword"]:
        alert= "Please verify that your current password is correct and that the new password matches the confirmation"
        conn.close()
        return render_template("changePassword.html", mensagem=alert)

    new_password_hashed = bcrypt.hashpw(updated_data["newPassword"].encode("utf-8"), bcrypt.gensalt())
    cursor.execute("UPDATE usuarios SET senha=? WHERE id=?", (new_password_hashed, user_id))
    conn.commit()
    conn.close()
    session.clear()

    return jsonify({"success": True})




############################################################ Route to your perfil page and other users perfil page  ############################################################
@bp.route("/user/<username>")
def user_perfil(username):
    user_id = session.get("usuario_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,) )
    user = cursor.fetchone()
    
    #Get the info to know if this perfil page from a friend of yours
    cursor.execute("""
    SELECT 1 FROM relationship
    WHERE ((usuario_id = ? AND amigo_id = ?) OR (usuario_id = ? AND amigo_id = ?))
    AND status == 'friends' """, (user_id, user['id'], user['id'], user_id))

    result = cursor.fetchone()
    if result:
        friends = True
    else:
        friends = False
    conn.close()
    if not user:
        return "Usuário não encontrado",  404

    return render_template("perfil-homepage.html", usuario=user, usuarioLogado=user_id, status=friends)


    
#Route to Recover Password
@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":   
        email = request.form("email")

        #Verify if email exists in DB
    

